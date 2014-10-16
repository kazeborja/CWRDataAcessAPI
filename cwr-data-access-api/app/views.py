from flask_restful import Resource, abort, Api
from flask.wrappers import Response
from flask.helpers import url_for
from flask import json
from flask import render_template
from app import app, cache
from app.services import AgreementService, AgreementTypeService, TerritoryService, SharesService, InterestedPartyService, \
    WorkService
from app.utils import JSONConverter, DictionaryList2ObjectList
from flask import request, redirect
from datetime import datetime
from functools import wraps
from model.models import Agreement, InterestedParty, Shares, Work


api = Api(app)

agreement_service = AgreementService()
agreement_type_service = AgreementTypeService()
interested_party_service = InterestedPartyService()
shares_service = SharesService()
territory_service = TerritoryService()
work_service = WorkService()

json_converter = JSONConverter()
list_converter = DictionaryList2ObjectList()


def make_cache_key():
    """
    Function that allows creating a unique id for every request
    There was a problem caching and changing arguments of the URL, so this is one possible solution

    :see: http://stackoverflow.com/questions/9413566/flask-cache-memoize-url-query-string-parameters-as-well
    """
    return request.url+str(request.headers.get('Accept'))


class AgreementListAPI(Resource):

    @staticmethod
    def get(page_number):
        agreements = agreement_service.paginate(1)

        return response_json_list(request, agreements)


class AgreementAddAPI(Resource):

    @staticmethod
    def post():

        for json_agreement in request.json:
            agreement = Agreement(json_agreement['agreement'])

            for json_territory in json_agreement['territories']:
                if json_territory['Inclusion/Exclusion indicator'] == 'I':
                    territory = territory_service.get_by_code(json_territory['TIS numeric code'])

                    if territory is not None:
                        agreement.add_territory(territory)

            for json_interested_party in json_agreement['interested_parties']:
                shares = Shares(json_interested_party)
                shares_service.insert(shares)

                ipa = InterestedParty(json_interested_party, shares.id)
                agreement.add_interested_party(ipa)

            agreement_service.insert(agreement)

        return {'URI': url_for('agreement_list', page_number=1)}, 201  # returns the URI for the new agreement


class AgreementByTypeAPI(Resource):

    @staticmethod
    def get(agr_type):
        agreements = agreement_service.get_agreements_by_type(agr_type)

        return response_json_list(request, agreements)


class AgreementAPI(Resource):

    @cache.cached(key_prefix=make_cache_key)
    def get(self, code):
        """
        Show country
        Response 200 OK
        """

        agreement = agreement_service.get_by_code(code)

        if agreement is None:
            abort(404)

        return response_json_item(agreement)

    @staticmethod
    def put(code):
        """
        If exists update country
        Response 204 NO CONTENT
        If not
        Response 400 BAD REQUEST
        """
        agreement = agreement_service.get_by_code(code)

        if agreement is not None:
            agreement = Agreement(request.json.get('attr_dict'))
            agreement.id = code
            agreement_service.update(agreement)
            return {}, 204
        else:
            abort(400)

    @staticmethod
    def delete(code):
        """
        Delete country
        Response 204 NO CONTENT
        """

        agreement_service.delete(code)
        return {}, 204


class AgreementTypeAPI(Resource):

    @staticmethod
    def get():
        agreement_types = agreement_type_service.get_all()

        return response_json_list(request, agreement_types)


class InterestedPartyAPI(Resource):

    @staticmethod
    def get(page_number):
        interested_parties = interested_party_service.paginate(page_number)

        return response_json_list(request, interested_parties)


class TerritoryListAPI(Resource):

    @staticmethod
    def get():
        territories = territory_service.get_all()

        return response_json_list(request, territories)


class TerritoryAPI(Resource):

    @staticmethod
    def get(code):
        territory = territory_service.get_by_iso2(code)

        return response_json_item(territory)


class WorkListAPI(Resource):

    @staticmethod
    def get():
        works = work_service.get_all()

        return response_json_list(request, works)

    @staticmethod
    def post():

        if request.json['ISWC'] is not None \
                and work_service.get_by_iswc(request.json['ISWC']) is None:
            work = Work(request.json)
            work_service.insert(work)

            return {'Error': False}, 201  # returns the URI for the new agreement
        else:
            return {'Error': True}, 201  # returns the URI for the new agreement

api.add_resource(AgreementListAPI, '/agreements/<page_number>', endpoint='agreement_list')
api.add_resource(AgreementAddAPI, '/agreements', endpoint='agreement_add')
api.add_resource(AgreementAPI, '/agreements/get/<code>', endpoint='agreement')
api.add_resource(AgreementTypeAPI, '/agreements/types', endpoint='agreement_types')
api.add_resource(AgreementByTypeAPI, '/agreements/<agr_type>', endpoint='agreements_by_type')
api.add_resource(TerritoryListAPI, '/territories', endpoint='territory_list')
api.add_resource(TerritoryAPI, '/territories/get/<code>', endpoint='territory')
api.add_resource(InterestedPartyAPI, '/ipas/<page_number>', endpoint="ipa_list")
api.add_resource(WorkListAPI, '/works', endpoint="works")


def response_json_list(request, collection):
    """
    Return response with the content in the format requested
    :type request: object
    Available formats:
    * JSON

    :param request: the request object
    :param collection: the collection to be converted
    :return: response in the requested format
    """
    
    def return_json():
        return Response(json_converter.list_to_json(collection), mimetype='application/json')

    functions = {
        'json': return_json,
    }

    functions_accept = {
        'application/json': return_json,
    }

    if request.args.get('format') in functions.keys():
        return functions[request.args.get('format')]()
    else:
        return (functions_accept[request.headers.get('Accept')]
                if request.headers.get('Accept') in functions_accept.keys() else functions['json'])()


def response_json_item(item):
    return Response(json_converter.object_to_json(item), mimetype='application/json')


def response_json_list(request, collection):
    """
    Return response with the content in the format requested
    Available formats:
    * JSON

    :param request: the request object
    :param collection: the collection to be converted
    :return: response in the requested format
    """
    def return_json():
        return Response(json_converter.list_to_json(collection), mimetype='application/json')

    functions = {
        'json': return_json,
    }

    functions_accept = {
        'application/json': return_json,
    }

    if request.args.get('format') in functions.keys():
        return functions[request.args.get('format')]()
    else:
        return (functions_accept[request.headers.get('Accept')]
                if request.headers.get('Accept') in functions_accept.keys() else functions['json'])()


def get_limit_and_offset():
    """
    Returns limit and offset in the request, if not provided limit=30 and offset=0

    :return: limit and offset
    """
    limit = int(request.args.get("limit")) if request.args.get("limit") is not None else 30
    offset = int(request.args.get("offset")) if request.args.get("offset") is not None else 0
    return limit, offset


def slice_by_limit_and_offset(elements_list, limit, offset):
    """
    Returns the sliced list
    """
    limit = limit + offset if (limit + offset) < len(elements_list) else len(elements_list)
    return elements_list[offset:limit]


class EmptyObject():
    """
    Class to create object without attributes, to be included dynamically
    """
    def __init__(self):
        pass