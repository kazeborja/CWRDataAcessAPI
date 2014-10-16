from app.utils import string_to_date

__author__ = 'Borja'

from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String, BOOLEAN, DATE, Float, Time
from sqlalchemy.orm import relationship, backref
from abc import abstractmethod
from app import db
import datetime


agreement_territory = db.Table('agreement_territory',
                               Column('agreement_id', Integer, ForeignKey('agreements.id')),
                               Column('territory_code', Integer, ForeignKey('territories.tis')))

agreement_ipa = db.Table('agreement_ipa',
                         Column('agreement_id', Integer, ForeignKey('agreements.id')),
                         Column('ipa_id', Integer, ForeignKey('interestedParties.id')))


class Agreement(db.Model):
    __tablename__ = 'agreements'
    id = Column(Integer, primary_key=True, autoincrement=True)
    submitter_agreement_number = Column(Integer, nullable=False)
    start_date = Column(DATE, nullable=False)
    end_date = Column(DATE)
    retention_end_date = Column(DATE)
    prior_royalty_status = Column(String(1), nullable=False)
    prior_royalty_start_date = Column(DATE)
    post_term_collection_status = Column(String(1), nullable=False)
    post_tem_collection_end_date = Column(DATE)
    signature_date = Column(DATE)
    works_number = Column(Integer, nullable=False)
    sales_manufacture_clause = Column(String(1))
    shares_change = Column(BOOLEAN)
    advance_given = Column(BOOLEAN)
    agreement_type_id = Column(String(2), ForeignKey('agreementTypes.id'), nullable=False)
    territories = relationship('Territory',
                               secondary=agreement_territory,
                               backref='agreements')
    interested_parties = relationship('InterestedParty',
                                      secondary=agreement_ipa,
                                      backref='agreements')

    def __init__(self, json):
        self.submitter_agreement_number = json['Submitter agreement number']
        self.start_date = string_to_date(json['Agreement start date'])
        self.end_date = string_to_date(json['Agreement end date'])
        self.retention_end_date = string_to_date(json['Retention end date'])
        self.prior_royalty_status = json['Prior royalty status']
        self.prior_royalty_start_date = string_to_date(json['Prior royalty start date'])
        self.post_term_collection_status = json['Post-term collection status']
        self.post_tem_collection_end_date = string_to_date(json['Post-term collection end date'])
        self.signature_date = string_to_date(json['Date of signature agreement'])
        self.works_number = json['Number of works']
        self.sales_manufacture_clause = json['Sales/Manufacture clause']
        self.shares_change = json['Shares change']
        self.advance_given = json['Advance given']
        self.agreement_type_id = json['Agreement type']

    def add_territory(self, territory):
        self.territories.append(territory)

    def add_interested_party(self, ipa):
        self.interested_parties.append(ipa)


class AgreementRole(db.Model):
    __tablename__ = 'agreementRoles'
    id = Column(String(2), primary_key=True, autoincrement=False)
    name = Column(String(20))
    description = Column(String(200))

    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description


class AgreementType(db.Model):
    __tablename__ = 'agreementTypes'
    id = Column(String(2), primary_key=True, autoincrement=False)
    name = Column(String(32))
    description = Column(String(500))

    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description


class CompositeType(db.Model):
    __tablename__ = 'compositeTypes'
    id = Column(String(3), primary_key=True, autoincrement=False)
    name = Column(String(50))
    description = Column(String(500))

    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description


class DistributionCategory(db.Model):
    __tablename__ = 'distributionCategories'
    id = Column(String(3), primary_key=True, autoincrement=False)
    name = Column(String(50))
    description = Column(String(500))

    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description


class ExcerptType(db.Model):
    __tablename__ = 'excerptTypes'
    id = Column(String(3), primary_key=True, autoincrement=False)
    name = Column(String(50))
    description = Column(String(500))

    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description


class InterestedParty(db.Model):
    __tablename__ = 'interestedParties'
    id = Column(Integer, primary_key=True, autoincrement=True)
    cae_number = Column(Integer, unique=True)
    ipi_number = Column(Integer)
    last_name = Column(String(45), nullable=False)
    writer_first_name = Column(String(30))
    role = Column(String(2), ForeignKey('agreementRoles.id'))
    shares_id = Column(Integer, ForeignKey('societyShares.id'))

    def __init__(self, json, shares_id):
        self.cae_number = json['Interested party CAE/IPI ID']
        self.ipi_number = None if int(json['IPI base number']) == 0 else int(json['IPI base number'])
        self.last_name = json['Interested party last name']
        self.writer_first_name = json['Interested party writer first name']
        self.role = json['Agreement role code']
        self.shares_id = shares_id


class LyricAdaptation(db.Model):
    __tablename__ = 'lyricAdaptations'
    id = Column(String(3), primary_key=True, autoincrement=False)
    name = Column(String(50))
    description = Column(String(500))

    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description


class MusicArrangement(db.Model):
    __tablename__ = 'musicArrangements'
    id = Column(String(3), primary_key=True, autoincrement=False)
    name = Column(String(50))
    description = Column(String(500))

    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description


class Shares(db.Model):
    __tablename__ = 'societyShares'
    id = Column(Integer, primary_key=True, autoincrement=True)
    pr_society_id = Column(Integer, ForeignKey('societies.id'))
    pr_share = Column(Float)
    mr_society_id = Column(Integer, ForeignKey('societies.id'))
    mr_share = Column(Float)
    sr_society_id = Column(Integer, ForeignKey('societies.id'))
    sr_share = Column(Float)

    def __init__(self, json):
        self.pr_society_id = json['PR affiliation society']
        self.pr_share = json['PR share']
        self.mr_society_id = json['MR affiliation society']
        self.mr_share = json['MR share']
        self.sr_society_id = json['SR affiliation society']
        self.sr_share = json['SR share']


class Society(db.Model):
    __tablename__ = 'societies'
    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(32), nullable=False)
    former_name = Column(String(32))

    def __init__(self, code, name, former_name):
        self.id = code
        self.name = name
        self.former_name = former_name


class Territory(db.Model):
    __tablename__ = 'territories'
    tis = Column(Integer, primary_key=True, autoincrement=False)
    iso2 = Column(String(2), unique=True)
    type = Column(String(20), nullable=False)
    name = Column(String(50), nullable=False, unique=True)
    official_name = Column(String(50))

    def __init__(self, tis, iso2=None, territory_type=None, name=None, official_name=None):
        self.tis = tis
        self.iso2 = iso2
        self.type = territory_type
        self.name = name
        self.official_name = official_name


class TextMusicRelationship(db.Model):
    __tablename__ = 'textMusicRelationships'
    id = Column(String(3), primary_key=True, autoincrement=False)
    name = Column(String(50))
    description = Column(String(500))

    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description


class VersionType(db.Model):
    __tablename__ = 'versionTypes'
    id = Column(String(3), primary_key=True, autoincrement=False)
    name = Column(String(50))
    description = Column(String(500))

    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description


class Work(db.Model):
    __tablename__ = 'works'
    id = Column(Integer, primary_key=True, autoincrement=True)
    iswc = Column(String(11))
    title = Column(String(60), nullable=False)
    lang_code = Column(String(2))
    duration = Column(Time)
    recorded_indicator = Column(String(1), nullable=False)
    grand_rights_indicator = Column(BOOLEAN)
    priority_flag = Column(String(1))
    distribution_category_id = Column(String(3), ForeignKey('distributionCategories.id'))
    text_music_relationship_id = Column(String(3), ForeignKey('textMusicRelationships.id'))
    composite_type_id = Column(String(3), ForeignKey('compositeTypes.id'))
    composite_component_count = Column(Integer)
    version_type_id = Column(String(3), ForeignKey('versionTypes.id'), nullable=False)
    excerpt_type_id = Column(String(3), ForeignKey('excerptTypes.id'))
    music_arrangement_id = Column(String(3), ForeignKey('musicArrangements.id'))
    lyric_adaptation_id = Column(String(3), ForeignKey('lyricAdaptations.id'))
    cwr_work_type_id = Column(String(2), ForeignKey('workTypes.id'))

    def __init__(self, json):
        self.iswc = json['ISWC']
        self.title = json['Work title']
        self.lang_code = json['Language code']
        self.recorded_indicator = json['Recorded indicator']
        self.grand_rights_indicator = json['Grand rights indicator']
        self.priority_flag = json['Priority flag']
        self.distribution_category_id = json['Musical work distribution category']
        self.text_music_relationship_id = json['Text music relationship']
        self.composite_type_id = json['Composite type']
        self.version_type_id = json['Version type']
        self.excerpt_type_id = json['Excerpt type']
        self.music_arrangement_id = json['Music arrangement']
        self.lyric_adaptation_id = json['Lyric adaptation']
        self.cwr_work_type_id = json['CWR work type']


class WorkType(db.Model):
    __tablename__ = 'workTypes'
    id = Column(String(2), primary_key=True, autoincrement=False)
    name = Column(String(50))

    def __init__(self, id, name):
        self.id = id
        self.name = name

# # TODO implement relationship tables
# work_publisher = db.Table('work_publisher',
#     Column('work_id', Integer(32), ForeignKey('works.id')),
#     Column('publisher_id', String(255), ForeignKey('indicators.id')),
#     Column('work_number', String(14)),
#     Column('contact_id', ))
#
#
# class Submitter(db.Model):
#     __tablename__ = 'submitters'
#     ipa_id = Column(Integer(32), ForeignKey('interestedParties.id'), nullable=False)
#     work_id = Column(Integer(32), ForeignKey('works.id'), nullable=False)
#
#
# submitter_agreement = db.Table('submitter_agreement',
#                                Column('agreement_it', Integer(32), ForeignKey('agreements.id')),
#                                Column('ipa_id', Integer(32), ForeignKey('interestedParties.id')),
#                                Column('publisher_id', Integer(32), ForeignKey('publishers.id')),
#                                Column('shares_id', Integer(32), ForeignKey('shares.id')))
#
#
# ipa_publisher = db.Table('ipa_publisher',
#                          Column('ipa_id', Integer(32), ForeignKey('interestedParties.id')),
#                          Column('publisher_id', Integer(32), ForeignKey('publishers.id')))
#
#
# class Publisher(db.Model):
#     __tablename__ = 'publishers'
#     id = Column(Integer(32), primary_key=True, autoincrement=True)
#     name = Column(String(45))
#     linked_to = Column(Integer(32), ForeignKey('publishers.id'))
#     tax_id = Column(Integer(9))
#     cae = Column(Integer(11))
#     reversionary_indicator = Column(BOOLEAN)
#     first_recording_indicator = Column(BOOLEAN)
#     ipi = Column(Integer(13), unique=True)
#     publisher_type = Column(String(2), ForeignKey('publisherTypes.id'))
#
#
# class PublisherType(db.Model):
#     __tablename__ = 'publisherTypes'
#     id = Column(String(2), primary_key=True, autoincrement=False)
#     name = Column(String(32))
#     description = Column(String(500))