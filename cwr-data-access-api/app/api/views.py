import json
from flask.wrappers import Response
from app.infrastructure.mongo_repos.Interested_party_repository import InterestedPartyRepository
from app.infrastructure.mongo_repos.agreement_repository import AgreementRepository
from flask import request, render_template, Flask
from app.infrastructure.mongo_repos.work_repository import WorkRepository
from commonworks.domain.models.agreement.interested_party import InterestedParty
from commonworks.domain.models.work.publisher import Publisher
from commonworks.domain.models.work.work import Work

app = Flask(__name__)

##########################################################################################
##                                 JSONP DECORATOR                                      ##
##########################################################################################
from commonworks.domain.models.agreement.agreement import Agreement


def JSONEncoder(request, data):
    json_item = json.dumps(data)

    callback = request.args.get('callback', False)

    if callback:
        return Response(str(callback) + '(' + str(json_item) + ');', mimetype="application/javascript")

    return Response(json_item, mimetype="application/json")

##########################################################################################
##                                        ROOT                                          ##
##########################################################################################


@app.route("/")
def index():
    """API Documentation"""
    return render_template('help.html')


def insert_agreements(agreements, submitter):
    agreement_list = []

    for json_agreement in agreements:
        if json_agreement['_rejected']:
            continue

        agreement = Agreement(submitter, json_agreement)

        territories_json = json_agreement['_territories']
        for territory_json in territories_json:
            if territory_json['_rejected']:
                continue

            agreement.add_territory(territory_json)

        interested_parties_json = json_agreement['_interested_parties']

        interested_parties = []
        for ipa_json in interested_parties_json:
            if interested_parties_json[ipa_json]['_rejected']:
                continue

            ipa = InterestedPartyRepository(
                url_root=request.url_root).find_ipa_by_submitter_id(submitter,
                                                                    interested_parties_json[ipa_json]['id'])

            if ipa is None:
                ipa = InterestedParty(submitter, interested_parties_json[ipa_json])
                agreement.add_interested_party(ipa.creation_id)
                ipa.add_agreement(agreement.creation_id, interested_parties_json[ipa_json])
                interested_parties.append(ipa)
            else:
                ipa_agreement = InterestedParty.create_ipa_agreement(agreement.creation_id,
                                                                     interested_parties_json[ipa_json])
                agreement.add_interested_party(ipa['_id'])
                InterestedPartyRepository(url_root=request.url_root).add_agreement(ipa['_id'], ipa_agreement)

        InterestedPartyRepository(url_root=request.url_root).insert_items(interested_parties)
        agreement_list.append(agreement)

    AgreementRepository(url_root=request.url_root).insert_items(agreement_list)


def insert_works(works, submitter, new_works=True):
    work_list = []
    for json_work in works:
        if json_work['_rejected']:
            continue

        work = WorkRepository(
            url_root=request.url_root).find_work_by_submitter_id(submitter, json_work['submitter_id'])

        if work is not None and new_works:
            # TODO: Remember to notify
            continue
        elif work is None and not new_works:
            continue

        work = Work(submitter, json_work)

        for publisher_json_reference in json_work['_publishers']:
            publisher_json = json_work['_publishers'][publisher_json_reference]
            if publisher_json['_rejected']:
                continue

            publisher = Publisher(submitter, publisher_json)

            """mongo_agreement = AgreementRepository(
                url_root=request.url_root).find_agreements_by_submitter_id(int(submitter), publisher.agreement_number)

            if mongo_agreement is None:
                continue

            publisher.mongo_agreement_id = mongo_agreement['_id']
            publisher.mongo_ipa_id = InterestedPartyRepository(
                url_root=request.url_root).find_ipa_by_submitter_id(int(submitter), publisher.interested_party_id)['_id']
            """
            work.add_publisher(publisher)

        if json_work['_entire_work_title'] is not None and not json_work['_entire_work_title']['_rejected']:
            work.set_entire_work_title(json_work['_entire_work_title'])

        if json_work['_recording_details'] is not None and not json_work['_recording_details']['_rejected']:
            work.set_recording_details(json_work['_recording_details'])

        if json_work['_version_original_title'] is not None and not json_work['_version_original_title']['_rejected']:
            work.set_original_work_title(json_work['_version_original_title'])

        if json_work['_work_origin'] is not None and not json_work['_work_origin']['_rejected']:
            work.set_original_work_title(json_work['_work_origin'])

        work_list.append(work)

    WorkRepository(url_root=request.url_root).insert_items(work_list)


@app.route("/initialize")
def initialize():
    AgreementRepository(url_root=request.url_root).drop_collection()
    InterestedPartyRepository(url_root=request.url_root).drop_collection()
    WorkRepository(url_root=request.url_root).drop_collection()

    with open('data.json') as json_data:
        json_document = json.load(json_data)

    if not json_document:
        raise Exception

    submitter = json_document['_header']['sender_id']
    groups = json_document['_groups']

    if groups[json_document['_group_types']['AGR']] is not None \
            and not groups[json_document['_group_types']['AGR']]['_rejected']:
        agreements = groups[json_document['_group_types']['AGR']]['_transactions']
        insert_agreements(agreements, submitter)

    if groups[json_document['_group_types']['NWR']] is not None \
            and not groups[json_document['_group_types']['NWR']]['_rejected']:
        print 'inserting new works'
        new_works = groups[json_document['_group_types']['NWR']]['_transactions']
        insert_works(new_works, submitter)

##########################################################################################
##                                     AGREEMENTS                                       ##
##########################################################################################


@app.route("/agreements")
def list_agreements():
    return list_agreements_page(0)


@app.route("/agreements/<page_number>")
def list_agreements_page(page_number):

    agreements = AgreementRepository(url_root=request.url_root).find_all(page_number)

    return JSONEncoder(request, agreements)


@app.route("/agreements/submitter/<submitter_id>/<agreement_number>")
def list_agreements_by_submitter_number(submitter_id, agreement_number):
    agreement = AgreementRepository(url_root=request.url_root).find_agreement_by_submitter_id(submitter_id,
                                                                                              agreement_number)

    return JSONEncoder(request, agreement)


@app.route("/agreements/ipa/<ipa_id>")
def agreements_by_ipa(ipa_id):

    agreements = AgreementRepository(url_root=request.url_root).find_agreements_by_ipa(ipa_id)

    return JSONEncoder(request, agreements)

##########################################################################################
##                                     AGREEMENTS                                       ##
##########################################################################################


@app.route("/interested_parties")
def list_interested_parties():
    return list_interested_parties_page(0)


@app.route("/interested_parties/<page_number>")
def list_interested_parties_page(page_number):

    interested_parties = InterestedPartyRepository(url_root=request.url_root).find_all(page_number)

    return JSONEncoder(request, interested_parties)

##########################################################################################
##                                     AGREEMENTS                                       ##
##########################################################################################


@app.route("/works")
def list_works():
    return list_works_page(0)


@app.route("/works/<page_number>")
def list_works_page(page_number):

    works = WorkRepository(url_root=request.url_root).find_all(page_number)

    return JSONEncoder(request, works)


@app.route("/works/id/<work_id>")
def find_work_by_id(work_id):
    work = WorkRepository(url_root=request.url_root).find_by_id(work_id)

    return JSONEncoder(request, work)

##########################################################################################
##                                        MAIN                                          ##
##########################################################################################

if __name__ == "__main__":
    app.debug = True
    app.run(port=5002)