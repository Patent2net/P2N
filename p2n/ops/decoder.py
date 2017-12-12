# -*- coding: utf-8 -*-
# (c) 2017 The Patent2Net Developers
import re
import logging
from copy import deepcopy
from collections import OrderedDict
from jsonpointer import JsonPointer, JsonPointerException
from p2n.util import to_list

logger = logging.getLogger(__name__)


class OPSExchangeDocumentDecoder:
    """
    Functions for decoding data from raw JSON OPS exchange documents.
    """

    pointer_country = JsonPointer('/exchange-document/@country')
    pointer_docnumber = JsonPointer('/exchange-document/@doc-number')
    pointer_kind = JsonPointer('/exchange-document/@kind')
    pointer_family_id = JsonPointer('/exchange-document/@family-id')

    pointer_application_reference = JsonPointer('/exchange-document/bibliographic-data/application-reference/document-id')
    pointer_publication_reference = JsonPointer('/exchange-document/bibliographic-data/publication-reference/document-id')
    pointer_abstract = JsonPointer('/exchange-document/abstract')
    pointer_applicant = JsonPointer('/exchange-document/bibliographic-data/parties/applicants/applicant')
    pointer_inventor = JsonPointer('/exchange-document/bibliographic-data/parties/inventors/inventor')

    pointer_invention_title = JsonPointer('/exchange-document/bibliographic-data/invention-title')

    pointer_ipc = JsonPointer('/exchange-document/bibliographic-data/classification-ipc/text')
    pointer_ipcr = JsonPointer('/exchange-document/bibliographic-data/classifications-ipcr/classification-ipcr')
    pointer_classifications = JsonPointer('/exchange-document/bibliographic-data/patent-classifications/patent-classification')


    @classmethod
    def document_number_date(cls, docref, id_type):
        """
        Decode document number and filing/grant date from
        /exchange-document/bibliographic-data/{application|publication}-reference/document-id.
        """
        docref_list = to_list(docref)
        for document_id in docref_list:
            if document_id['@document-id-type'] == id_type:
                if id_type == 'epodoc':
                    doc_number = document_id['doc-number']['$']
                else:
                    doc_number = document_id['country']['$'] + document_id['doc-number']['$'] + document_id['kind']['$']
                date = document_id.get('date', {}).get('$')
                date = cls.decode_date(date)
                return doc_number, date
        return None, None

    @staticmethod
    def decode_date(date):
        date = date and '-'.join([date[:4], date[4:6], date[6:8]])
        return date

    @classmethod
    def titles(cls, data):
        """
        Decode titles in all languages.
        """

        try:
            titles = to_list(cls.pointer_invention_title.resolve(data))
        except JsonPointerException:
            return {}

        data = OrderedDict()
        for title in titles:
            language = title.get(u'@lang', u'ol')
            value = title[u'$'] or u''
            if value:
                data[language] = value
        return data

    @classmethod
    def abstracts(cls, data):
        """
        Decode abstracts in all languages.
        """

        try:
            abstracts = to_list(cls.pointer_abstract.resolve(data))
        except JsonPointerException:
            return {}

        data = OrderedDict()
        for abstract in abstracts:
            language = abstract.get(u'@lang', u'ol')

            lines = to_list(abstract['p'])
            lines = map(lambda line: line['$'], lines)
            value = '\n'.join(lines)

            if value:
                data[language] = value

        return data

    @classmethod
    def parties(cls, partylist, name):
        """
        Decode list of applicants or inventors.
        """
        #print 'partylist:', partylist
        parties = []
        for party in partylist:

            # Use only "epodoc" party members, as they contain the origin country
            if party['@data-format'] != 'epodoc':
                continue

            epodoc_name = party[name]['name']['$'].replace(u'\u2002', u' ')
            matches = re.match('(?P<name>.+?) \[(?P<country>.+?)\]', epodoc_name)
            if matches:
                parties.append(matches.groupdict())
            else:
                parties.append({'country': None, 'name': epodoc_name})

        return parties

    @classmethod
    def applicants(cls, data):
        try:
            nodes = to_list(cls.pointer_applicant.resolve(data))
        except JsonPointerException:
            return []
        return cls.parties(nodes, 'applicant-name')

    @classmethod
    def inventors(cls, data):
        try:
            nodes = to_list(cls.pointer_inventor.resolve(data))
        except JsonPointerException:
            return []
        return cls.parties(nodes, 'inventor-name')


    @classmethod
    def classifications_ipc(cls, data):

        try:
            entries = to_list(cls.pointer_ipc.resolve(data))
        except JsonPointerException:
            return []

        entries = map(lambda entry: entry['$'], entries)

        return entries


    @classmethod
    def classifications_ipcr(cls, data):

        try:
            entries = to_list(cls.pointer_ipcr.resolve(data))
        except JsonPointerException:
            return []

        entries = map(lambda entry: entry['text']['$'], entries)
        entries = map(lambda entry: entry[:15].replace(' ', ''), entries)

        return entries

    @classmethod
    def classifications_more(cls, data):

        try:
            nodes = to_list(cls.pointer_classifications.resolve(data))
        except JsonPointerException:
            return {}

        cpc_fieldnames = ['section', 'class', 'subclass', 'main-group', '/', 'subgroup'];

        classifications = {}
        for node in nodes:
            scheme = node['classification-scheme']['@scheme']

            classifications.setdefault(scheme, [])

            entry = None
            if scheme == 'CPC' or scheme == 'CPCNO':
                entry_parts = []
                for cpc_fieldname in cpc_fieldnames:
                    if cpc_fieldname == '/':
                        entry_parts.append('/')
                        continue
                    if node[cpc_fieldname]:
                        part = node[cpc_fieldname]['$']
                        entry_parts.append(part)
                    else:
                        logger.warning('Unknown CPC classification field "{cpc_fieldname}"'.format(**locals()))
                entry = ''.join(entry_parts)

            elif scheme == 'UC' or scheme == 'FI' or scheme == 'FTERM':
                # UC was sighted with US documents, FI and FTERM with JP documents
                entry = node['classification-symbol']['$']

            else:
                logger.warning('Unknown classification scheme "{scheme}"'.format(**locals()))

            if entry:
                classifications[scheme].append(entry)

        return classifications



class OPSRegisterDocumentDecoder:
    """
    Functions for decoding data from raw JSON OPS register documents.
    """

    pointer_status = JsonPointer('/reg:register-document/@status')
    pointer_designated_states = JsonPointer('/reg:register-document/reg:bibliographic-data/reg:designation-of-states')
    pointer_applicants = JsonPointer('/reg:register-document/reg:bibliographic-data/reg:parties/reg:applicants')
    pointer_inventors = JsonPointer('/reg:register-document/reg:bibliographic-data/reg:parties/reg:inventors')
    pointer_agents = JsonPointer('/reg:register-document/reg:bibliographic-data/reg:parties/reg:agents')
    pointer_actions = JsonPointer('/reg:register-document/reg:bibliographic-data/reg:dates-rights-effective')
    pointer_filing_language = JsonPointer('/reg:register-document/reg:bibliographic-data/reg:language-of-filing/$')

    """
    TODO:

    # EP88402018P
    u'reg:dates-rights-effective': {u'reg:first-examination-report-despatched': {u'reg:date': {u'$': u'19901213'}},
                                    u'reg:request-for-examination': {u'@change-gazette-num': u'1989/41',
                                                                     u'reg:date': {u'$': u'19890628'}}},

    # EP86400204P
    u'reg:opposition-data': {u'@change-date': u'19890321',
                             u'@change-gazette-num': u'1989/19',
                             u'reg:opposition-not-filed': {u'reg:date': {u'$': u'19890221'}}},

    # EP06823909P
    u'reg:date-application-deemed-withdrawn': {u'@change-gazette-num': u'2009/11',
                                               u'reg:date': {u'$': u'20080909'}},

    # EP10806019P
    u'reg:date-application-withdrawn-by-applicant': {u'@change-gazette-num': u'2012/35'},


    # EP08836401P
    u'reg:term-of-grant': [{u'@change-date': u'20140718',
                            u'@change-gazette-num': u'2014/34',
                            u'reg:lapsed-in-country': [{u'reg:country': {u'$': u'HU'},
                                                        u'reg:date': {u'$': u'20080709'}},
                                                       {u'reg:country': {u'$': u'AT'},
                                                        u'reg:date': {u'$': u'20120418'}},

    # EP16202765P
    u'reg:related-documents': {u'reg:division': {u'reg:relation': {u'reg:child-doc': {u'reg:document-id': {u'reg:country': {u'$': u''},
           u'reg:doc-number': {u'$': u''}}},


    # EP14879896P
    u'reg:office-specific-bib-data':


    # EP14879896P
    u'reg:ep-patent-statuses': {u'reg:ep-patent-status': [{u'$': u'The application is deemed to be withdrawn',
       u'@change-date': u'20170714',
       u'@status-code': u'10'},
      {u'$': u'The international publication has been made',
       u'@change-date': u'20161115',
       u'@status-code': u'17'}]}}}


    """

    @classmethod
    def status(cls, data):
        """
        Decode register status.
        """
        return cls.pointer_status.resolve(data)


    @classmethod
    def filing_language(cls, data):
        """
        Decode filing language.
        """
        return cls.pointer_filing_language.resolve(data)


    @classmethod
    def actions(cls, data):
        try:
            actions = []
            for key, value in cls.pointer_actions.resolve(data).iteritems():
                entry = {
                    'name': key.replace('reg:', ''),
                    'date': OPSExchangeDocumentDecoder.decode_date(value['reg:date']['$']),
                    }
                actions.append(entry)
            return actions
        except JsonPointerException:
            return []

    @classmethod
    def designated_states(cls, data):
        """
        Decode designated states from register document.

        # TODO: Multiple designated states entries. e.g. EP16202765P
        """

        try:
            nodes = to_list(cls.pointer_designated_states.resolve(data))
        except JsonPointerException:
            return []

        return cls.read_history(nodes, 'reg:designation-pct', cls.countries)

    @classmethod
    def countries(cls, entry):
        """
        Decode list of countries (designated states).
        """

        countries_pointer = JsonPointer('/reg:regional/reg:country')
        countries_raw = to_list(countries_pointer.resolve(entry[0]))
        countries = [country_raw['$'] for country_raw in countries_raw]
        return countries

    @classmethod
    def applicants(cls, data):
        """
        Decode list of applicants
        """
        try:
            nodes = to_list(cls.pointer_applicants.resolve(data))
        except JsonPointerException:
            return []

        return cls.read_history(nodes, 'reg:applicant', cls.parties)

    @classmethod
    def inventors(cls, data):
        """
        Decode list of inventors
        """
        try:
            nodes = to_list(cls.pointer_inventors.resolve(data))
        except JsonPointerException:
            return []

        return cls.read_history(nodes, 'reg:inventor', cls.parties)

    @classmethod
    def agents(cls, data):
        """
        Decode list of agents
        """
        try:
            nodes = to_list(cls.pointer_agents.resolve(data))
        except JsonPointerException:
            return []

        return cls.read_history(nodes, 'reg:agent', cls.parties)

    @classmethod
    def parties(cls, partylist):
        """
        Decode list of applicants, inventors or agents.
        """
        entries = []
        for party in partylist:

            addressbook = party['reg:addressbook']

            entry = OrderedDict()
            entry['name'] = addressbook['reg:name']['$']
            entry['country'] = addressbook['reg:address']['reg:country']['$']
            address = []
            for index in range(1, 7):
                fieldname = 'address-{}'.format(index)
                fieldname_ops = 'reg:{}'.format(fieldname)
                try:
                    value = addressbook['reg:address'][fieldname_ops]['$']
                    address.append(value)
                except KeyError:
                    pass

            entry['address'] = address

            entries.append(entry)

        return entries


    @classmethod
    def read_history(cls, nodes, node_name, item_decoder):
        """
        Generically decode arbitrary lists based on the @change-date / @change-gazette-num scheme
        """

        # Collect entries over time
        history = []
        for node in nodes:
            entry = OrderedDict()
            entry['change_date'] = OPSExchangeDocumentDecoder.decode_date(node['@change-date'])
            entry['change_gazette'] = node['@change-gazette-num']
            entry['items'] = item_decoder(to_list(node[node_name]))
            history.append(entry)

        # Deduplicate entries. Sometimes, duplicate entries are in the history list,
        # one with 'change_gazette' == 'N/P' and another one with a real value, e.g. '1986/34'.
        # We want to choose the entry with the real value and suppress to other one,
        # but only if all the bibliographic data are equal.
        deduplicated = []
        real = []
        for entry in history:
            entry_dup = deepcopy(entry)
            del entry_dup['change_gazette']

            if deduplicated:
                overwrite = (real[-1]['change_gazette'] == 'N/P' and real[-1]['change_date'] == entry['change_date']) and (deduplicated[-1] == entry_dup)
                if overwrite:
                    real.pop()
                    deduplicated.pop()

            if entry_dup not in deduplicated:
                deduplicated.append(entry_dup)
                real.append(entry)

        return real
