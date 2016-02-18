from binascii import hexlify
from bs4 import BeautifulSoup
from datetime import datetime
import logging
import logging.config
import html

from ecolex.management.commands.logging import LOG_DICT
from ecolex.management.utils import EcolexSolr, TREATY, get_content_from_url
from ecolex.management.utils import get_file_from_url
from ecolex.management.utils import format_date

logging.config.dictConfig(LOG_DICT)
logger = logging.getLogger('import')

DOCUMENT = 'document'
PARTY = 'party'
COUNTRY = 'country'
TOTAL_DOCS = 'numberresultsfound'
NULL_DATE = format_date('0000-00-00')
B7 = 'International Environmental Law – Multilateral Agreements'
URL_CHANGE_FROM = 'http://www.ecolex.org/server2.php/server2neu.php/'
URL_CHANGE_TO = 'http://www.ecolex.org/server2neu.php/'
replace_url = lambda text: (URL_CHANGE_TO + text.split(URL_CHANGE_FROM)[-1]) if text.startswith(URL_CHANGE_FROM) else text

FIELD_MAP = {
    'recid': 'trElisId',
    'informeauid': 'trInformeaId',
    'dateofentry': 'trDateOfEntry',
    'dateofmodification': 'trDateOfModification',
    'dateoftext': 'trDateOfText',
    'searchdate': 'trSearchDate',

    'titleoftext': 'trPaperTitleOfText_en',
    'titleoftextsp': 'trPaperTitleOfText_es',
    'titleoftextfr': 'trPaperTitleOfText_fr',
    'titleoftextother': 'trPaperTitleOfText_other',

    'typeoftext': 'trTypeOfText_en',
    'typeoftext_es_es': 'trTypeOfText_es',
    'typeoftext_fr_fr': 'trTypeOfText_fr',

    'jurisdiction': 'trJurisdiction_en',
    'jurisdiction_es_es': 'trJurisdiction_es',
    'jurisdiction_fr_fr': 'trJurisdiction_fr',

    'fieldofapplication': 'trFieldOfApplication_en',
    'fieldofapplication_fr_fr': 'trFieldOfApplication_fr',
    'fieldofapplication_es_es': 'trFieldOfApplication_es',

    'subject': 'trSubject_en',
    'subject_es_es': 'trSubject_es',
    'subject_fr_fr': 'trSubject_fr',

    'languageofdocument': 'trLanguageOfDocument_en',
    'languageofdocument_es_es': 'trLanguageOfDocument_es',
    'languageofdocument_fr_fr': 'trLanguageOfDocument_fr',
    'obsolete': 'trObsolete',
    'enabledbytreaty': 'trEnabledByTreaty',
    'placeofadoption': 'trPlaceOfAdoption',

    'depository': 'trDepository_en',
    'depository_fr': 'trDepository_fr',
    'depository_es': 'trDepository_es',

    'entryintoforcedate': 'trEntryIntoForceDate',
    'keyword': 'trKeyword_en',
    'keyword_es_es': 'trKeyword_es',
    'keyword_fr_fr': 'trKeyword_fr',

    'abstract': 'trAbstract_en',
    'abstractEs': 'trAbstract_es',
    'abstractFr': 'trAbstract_fr',

    'comment': 'trComment',
    'titleoftextshort': 'trTitleOfTextShort',
    'author': 'trAuthor',
    'titleabbreviation': 'trTitleAbbreviation',
    'placeofadoption': 'trPlaceOfAdoption',

    'basin': 'trBasin_en',
    'basin_fr_fr': 'trBasin_fr',
    'basin_es_es': 'trBasin_es',

    'citiestreaty': 'trCitiesTreaty',
    'confname': 'trConfName',
    'contributor': 'trContributor',
    'courtname': 'trCourtName',
    'dateoflastlegalaction': 'trDateOfLastLegalAction',

    'linktofulltext': 'trLinkToFullText_en',
    'linktofulltextsp': 'trLinkToFullText_es',
    'linktofulltextfr': 'trLinkToFullText_fr',
    'linktofulltextother': 'trLinkToFullText_other',

    'linktoabstract': 'trLinkToAbstract',
    'obsolete': 'trObsolete',
    'region': 'trRegion',
    'relevanttexttreaty': 'trRelevantTextTreaty',
    'scope': 'trScope',
    'searchdate': 'trSearchDate',
    'seatofcourt': 'trSeatOfCourt',
    'supersedestreaty': 'trSupersedesTreaty',
    'amendstreaty': 'trAmendsTreaty',
    'citestreaty': 'trCitesTreaty',
    'availablein': 'trAvailableIn',
    'languageoftranslation': 'trLanguageOfTranslation',
    'numberofpages': 'trNumberOfPages',
    'officialPublication': 'trOfficialPublication',
    'InternetReference': 'trInternetReference_en',
    'InternetReferenceFr': 'trInternetReference_fr',
    'InternetReferenceEs': 'trInternetReference_es',
    'InternetReferenceOther': 'trInternetReference_other',

    'dateofconsolidation': 'trDateOfConsolidation',
}

PARTICIPANT_FIELDS = {
    'country': 'partyCountry',
    'entryintoforce': 'partyEntryIntoForce',
    'dateofratification': 'partyDateOfRatification',
    'dateofaccessionapprobation': 'partyDateOfAccessionApprobation',
    'dateofacceptanceapproval': 'partyDateOfAcceptanceApproval',
    'dateofconsenttobebound': 'partyDateOfConsentToBeBound',
    'dateofsuccession': 'partyDateOfSuccession',
    'dateofdefinitesignature': 'partyDateOfDefiniteSignature',
    'dateofsimplesignature': 'partyDateOfSimpleSignature',
    'dateofprovisionalapplication': 'partyDateOfProvisionalApplication',
    'dateofparticipation': 'partyDateOfParticipation',
    'dateofdeclaration': 'partyDateOfDeclaration',
    'dateofreservation': 'partyDateOfReservation',
    'dateofwithdrawal': 'partyDateOfWithdrawal',
}


DATE_FIELDS = [
    'trDateOfEntry',
    'trDateOfModification',
    'trDateOfText',
    'trSearchDate',
    'trEntryIntoForceDate',
    'trDateOfLastLegalAction',
    'trSearchDate',
    'trDateOfConsolidation',
    'partyEntryIntoForce',
    'partyDateOfRatification',
    'partyDateOfAccessionApprobation',
    'partyDateOfAcceptanceApproval',
    'partyDateOfConsentToBeBound',
    'partyDateOfSuccession',
    'partyDateOfDefiniteSignature',
    'partyDateOfSimpleSignature',
    'partyDateOfProvisionalApplication',
    'partyDateOfParticipation',
    'partyDateOfDeclaration',
    'partyDateOfReservation',
    'partyDateOfWithdrawal',
]

REFERENCE_MAPPING = {
    'trEnabledByTreaty': 'trEnablesTreaty',
    'trAmendsTreaty': 'trAmendedBy',
    'trSupersedesTreaty': 'trSupersededBy',
    'trCitesTreaty': 'trCitedBy',
}

URL_FIELDS = [
    'linktofulltext', 'linktofulltextsp', 'linktofulltextfr',
    'linktofulltextother'
]


class Treaty(object):

    def __init__(self, data, solr):
        self.data = data
        self.solr = solr
        self.update_field = 'trDateOfModification'
        self.date_format = '%Y-%m-%dT%H:%M:%SZ'
        self.elis_id = 'trElisId'

    def is_modified(self, old_treaty):
        old_date = datetime.strptime(old_treaty[self.update_field],
                                     self.date_format)
        new_date = datetime.strptime(self.data[self.update_field][0],
                                     self.date_format)
        if old_date < new_date:
            logger.info('Update on %s' % (self.data[self.elis_id]))
            return True
        logger.info('No update on %s' % (self.data[self.elis_id]))
        return False

    def get_solr_format(self, elis_id, solr_id):
        if solr_id:
            self.data['id'] = solr_id
        return self.data


class TreatyImporter(object):
    CUSTOM_RULES = [
        {
            'condition_field': 'trElisId',
            'condition_value': 'TRE-146817',
            'action_field': 'trFieldOfApplication_en',
            'action_value': ['Global', 'Regional/restricted'],
        },
        {
            'condition_field': 'trElisId',
            'condition_value': 'TRE-149349',
            'action_field': 'trDateOfText',
            'action_value': format_date('2009-10-02'),
        },
    ]

    def __init__(self, config):
        self.solr_timeout = config.getint('solr_timeout')
        self.treaties_url = config.get('treaties_url')
        self.import_field = config.get('import_field')
        self.query_format = config.get('query_format')
        self.query_filter = config.get('query_filter')
        self.query_export = config.get('query_export')
        self.query_skip = config.get('query_skip')
        self.query_type = config.get('query_type')
        self.per_page = int(config.get('per_page'))
        self.start_year = int(config.get('start_year'))
        now = datetime.now()
        self.end_year = config.getint('end_year', now.year)
        self.start_month = int(config.get('start_month', now.month))
        self.end_month = int(config.get('end_month', now.month))
        self.solr = EcolexSolr(self.solr_timeout)
        logger.info('Started treaty importer')

    def harvest(self, batch_size):

        year = self.end_year
        while year >= self.start_year:
            raw_treaties = []

            for month in range(self.start_month, self.end_month+1):
                skip = 0
                url = self._create_url(year, month, skip)
                content = get_content_from_url(url)
                bs = BeautifulSoup(content)
                if bs.find('error'):
                    logger.info('For %d/%d found 0 treaties' % (month, year))
                    continue

                total_docs = int(bs.find('result').attrs[TOTAL_DOCS])
                found_docs = len(bs.findAll(DOCUMENT))
                raw_treaties.append(content)
                logger.info(url)
                logger.info('For: %d/%d found: %d treaties' %
                            (month, year, total_docs))
                if total_docs > found_docs:
                    while skip < total_docs - found_docs:
                        skip += found_docs
                        url = self._create_url(year, month, skip)
                        content = get_content_from_url(url)
                        bs = BeautifulSoup(content)
                        if bs.find('error'):
                            logger.error(url)
                        raw_treaties.append(content)

            logger.debug('Parsing %d pages' % (len(raw_treaties)))
            treaties = self._parse(raw_treaties)
            logger.debug('Pre-processing %d treaties' % (len(treaties)))
            self._clean_referred_treaties(treaties)
            self._add_back_links(treaties)
            new_treaties = filter(bool, [self._get_solr_treaty(treaty) for
                                         treaty in treaties.values()])
            logger.debug('Adding treaties')
            try:
                self.solr.add_bulk(new_treaties)
                year -= 1
            except:
                logger.exception('Error updating records, retrying')

        logger.info('Finished harvesting treaties')

    def _parse(self, raw_treaties):
        treaties = {}
        for raw_treaty in raw_treaties:
            bs = BeautifulSoup(raw_treaty)
            for document in bs.findAll(DOCUMENT):
                data = {
                    'type': TREATY,
                }

                for k, v in FIELD_MAP.items():
                    field_values = document.findAll(k)
                    if field_values:
                        data[v] = [self._clean_text(f.text) for
                                   f in field_values]
                        if v in DATE_FIELDS:
                            data[v] = [format_date(date) for date in data[v]
                                       if self._valid_date(date)]

                for party in document.findAll(PARTY):
                    if not getattr(party, COUNTRY):
                        continue
                    for k, v in PARTICIPANT_FIELDS.items():
                        field = getattr(party, k)
                        if v not in data:
                            data[v] = []
                        if field:
                            clean_field = self._clean_text(field.text)
                            data[v].append(self._party_format_date(clean_field)
                                           if v in DATE_FIELDS
                                           else clean_field)
                        else:
                            data[v].append(NULL_DATE)

                for party_field in PARTICIPANT_FIELDS.values():
                    if party_field not in data:
                        continue
                    if all([d == NULL_DATE for d in data[party_field]]):
                        data[party_field] = None

                data['text'] = ''
                for field in URL_FIELDS:
                    value = document.find(field)
                    if value:
                        # TODO: this is duplicated code (see _apply_custom_rules).
                        # PDF's should not be parsed and indexed at this stage
                        url = replace_url(value.text)
                        logger.debug('Getting file %s.' %url)
                        try:
                            file_obj = get_file_from_url(url)
                            data['text'] += self.solr.extract(file_obj)
                        except:
                            logger.exception('Error indexing file %s.' %url)

                elis_id = data['trElisId'][0]
                data['trElisId'] = elis_id

                data = self._apply_custom_rules(data)

                treaties[elis_id] = data

        return treaties

    def _apply_custom_rules(self, data):
        for rule in self.CUSTOM_RULES:
            value = data.get(rule['condition_field'], '')
            if value == rule['condition_value']:
                data[rule['action_field']] = rule['action_value']

        available_in = data.get('trAvailableIn', [])
        new_available_in = []
        for publication in available_in:
            if publication.startswith('B7'):
                new_available_in.append(publication.replace('B7', B7))
        data['trAvailableIn'] = new_available_in

        # fix server2.php/server2neu.php in full text links
        field_names = ['trLinkToFullText_en', 'trLinkToFullText_es', 'trLinkToFullText_fr', 'trLinkToFullText_other']
        for key, value in data.items():
            if key in field_names:
                data[key] = list(map(replace_url, data[key]))
        return data

    def _get_solr_treaty(self, treaty_data):
        new_treaty = Treaty(treaty_data, self.solr)
        existing_treaty = self.solr.search(TREATY, treaty_data['trElisId'])
        if not existing_treaty:
            logger.info('Insert on %s' % (treaty_data['trElisId']))
        elif not new_treaty.is_modified(existing_treaty):
            return None
        solr_id = existing_treaty['id'] if existing_treaty else None
        return new_treaty.get_solr_format(treaty_data['trElisId'], solr_id)

    def _clean_text(self, text):
        return html.unescape(text.strip())

    def _valid_date(self, date):
        date_info = date.split('-')
        if len(date_info) != 3:
            return False
        if (date_info[0] == '0000' or date_info[1] == '00'
                or date_info[2] == '00'):
            return False
        return True

    def _party_format_date(self, date):
        if date == '':
            return date
        date_fields = date.split('-')
        for i in range(3 - len(date_fields)):
            date += "-01"
        return format_date(date)

    def _clean_referred_treaties(self, solr_docs):
        for elis_id, doc in solr_docs.items():
            # Remove references not present in solr_docs
            # for field_name in REFERENCE_MAPPING:
            #     if field_name in doc:
            #         doc[field_name] = [ref for ref in doc[field_name]
            #                            if ref in solr_docs]
            # Remove empty properties
            solr_docs[elis_id] = dict((k, v)
                                      for k, v in solr_docs[elis_id].items()
                                      if not isinstance(v, list) or any(v))

    def _add_back_links(self, solr_docs):
        for elis_id, doc in solr_docs.items():
            for orig_field, backlink_field in REFERENCE_MAPPING.items():
                if orig_field in doc:
                    for ref in doc[orig_field]:
                        if ref in solr_docs:
                            solr_docs[ref].setdefault(backlink_field, [])
                            solr_docs[ref][backlink_field].append(elis_id)
                        else:
                            # TODO: what if link is not present in solr_docs?
                            existing_treaty = self.solr.search(TREATY, ref)
                            if existing_treaty:
                                logger.warn('Backlink on %s to %s should be updated' % (ref, elis_id))
                                # TODO
                            else:
                                logger.warn('%s does not exist in Solr in order to update backlink to %s' % (ref, elis_id))

    def _create_url(self, year, month, skip):
        query_year = self.query_format % (year, month)
        query_hex = hexlify(str.encode(query_year)).decode()
        query = self.query_filter % (query_hex)
        page = self.query_skip % (skip)

        url = '%s%s%s%s%s' % (self.treaties_url, self.query_export, query,
                              self.query_type, page)
        return url

    def update_status(self):
        rows = 50
        index = 0
        treaties = []
        while True:
            print(index)
            docs = self.solr.solr.search('type:treaty', rows=rows, start=index)
            for treaty in docs:
                if 'trEntryIntoForceDate' not in treaty:
                    treaty['trStatus'] = 'Not in force'
                else:
                    if 'trSupersededBy' in treaty:
                        treaty['trStatus'] = 'Superseded'
                    else:
                        treaty['trStatus'] = 'In force'
                treaties.append(treaty)

            if len(docs) < rows:
                break
            index += rows
        self.solr.add_bulk(treaties)

    def test(self):
        pass
