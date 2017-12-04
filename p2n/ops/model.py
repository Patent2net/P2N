# -*- coding: utf-8 -*-
# (c) 2017 The Patent2Net Developers
import re
import json
import logging
from copy import deepcopy
from collections import OrderedDict
from jsonpointer import JsonPointer, JsonPointerException
from p2n.util import to_list

logger = logging.getLogger(__name__)


class OPSBiblioSearchResponse:
    """
    Read the response from OPS published data search and decode the
    search results to a list of OPSExchangeDocument objects.
    """

    # Some JSON pointers for accessing the innards of "ops:biblio-search" responses
    pointer_results = JsonPointer('/ops:world-patent-data/ops:biblio-search/ops:search-result/exchange-documents')
    pointer_total_count = JsonPointer('/ops:world-patent-data/ops:biblio-search/@total-result-count')
    pointer_range = JsonPointer('/ops:world-patent-data/ops:biblio-search/ops:range')

    def __init__(self, data):
        self.data = data
        self.results = []
        self.read()

    @property
    def total_result_count(self):
        """
        Extract total result count from response.
        """
        return int(self.pointer_total_count.resolve(self.data))

    def read(self):
        """
        Read list of result documents from response and create
        list of OPSExchangeDocument objects inside ``self.results``.
        """
        exchange_documents = to_list(self.pointer_results.resolve(self.data))
        for exchange_document in exchange_documents:
            item = OPSExchangeDocument()
            item.read(exchange_document)
            self.results.append(item)

    def merge_results(self, chunk):
        """
        Merge results from another response chunk into the main list of results.
        This is used for crawling across all results from a search response
        when fetching chunks of 100 result documents each, as this is the
        maximum page size with the OPS API.
        """

        # Merge result documents of chunk into main list of results
        main_results = to_list(self.pointer_results.resolve(self.data))
        chunk_results = to_list(self.pointer_results.resolve(chunk))
        main_results += chunk_results

        # Amend result data
        self.pointer_results.set(self.data, main_results, inplace=True)

        # Amend metadata
        new_total_count = str(len(main_results))
        self.pointer_total_count.set(self.data, new_total_count)
        self.pointer_range.set(self.data, {'@begin': '1', '@end': new_total_count})


class OPSFamilyResponse:
    """
    Read the response from OPS family retrieval and decode the
    results to a list of OPSExchangeDocument objects.
    """

    def __init__(self, data):
        self.data = data
        self.results = []
        self.read()

    def read(self):
        pointer_results = JsonPointer('/ops:world-patent-data/ops:patent-family/ops:family-member')
        family_members = to_list(pointer_results.resolve(self.data))
        for family_member in family_members:

            # Decode document number
            publication_number = 'unknown'
            try:
                document_id = JsonPointer('/publication-reference/document-id')
                publication_number, publication_date = OPSExchangeDocument.decode_document_number_date(document_id.resolve(family_member), 'epodoc')
            except:
                pass

            # Read bibliographic data for family member
            item = OPSExchangeDocument()
            try:
                item.read(family_member)
                self.results.append(item)
            except JsonPointerException:
                logger.warning('No bibliographic data for family member "{}"'.format(publication_number))


class OPSRegisterResponse:
    """
    Read the response from OPS register information retrieval and decode the
    results to a list of OPSRegisterDocument objects.
    """

    def __init__(self, data):
        self.data = data
        self.results = []
        self.read()

    def read(self):
        pointer_results = JsonPointer('/ops:world-patent-data/ops:register-search/reg:register-documents')
        register_documents = to_list(pointer_results.resolve(self.data))
        for register_document in register_documents:
            item = OPSRegisterDocument()
            try:
                item.read(register_document)
                self.results.append(item)
            except JsonPointerException:
                logger.warning('Could not read register information from data "{}"'.format(register_document))


class OPSExchangeDocument:
    """
    Implement the data model of OPS exchange documents,
    optionally enriched by register information.
    """

    def __init__(self):

        # Bibliographic data
        self.application_date = None
        self.application_number_docdb = None
        self.application_number_epodoc = None

        self.publication_date = None
        self.publication_number_docdb = None
        self.publication_number_epodoc = None

        self.country = None
        self.document_number = None
        self.family_id = None
        self.title = {}
        self.abstract = None
        self.applicants = []
        self.inventors = []

        # Register information
        self.register = None
        self.designated_states = []

    def as_dict(self):
        return deepcopy(self.__dict__)

    def to_json(self, pretty=False):
        """Convert document to JSON format"""
        if pretty:
            return json.dumps(self.as_dict(), indent=4)
        else:
            return json.dumps(self.as_dict())

    @staticmethod
    def decode_document_number_date(docref, id_type):
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
                date = date and '-'.join([date[:4], date[4:6], date[6:8]])
                return doc_number, date
        return None, None

    @staticmethod
    def decode_titles(titles):
        """
        Decode titles in all languages.
        """
        data = OrderedDict()
        for title in titles:
            language = title.get(u'@lang', u'ol')
            value = title[u'$'] or u''
            if value:
                data[language] = value
        return data

    @staticmethod
    def decode_abstracts(abstracts):
        """
        Decode abstracts in all languages.
        """
        data = OrderedDict()
        for abstract in abstracts:
            language = abstract.get(u'@lang', u'ol')

            lines = to_list(abstract['p'])
            lines = map(lambda line: line['$'], lines)
            value = '\n'.join(lines)

            if value:
                data[language] = value

        return data

    @staticmethod
    def decode_parties(partylist, name):
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

        return parties

    def read(self, data):
        """
        Read information from data object.
        """

        pointer_country = JsonPointer('/exchange-document/@country')
        pointer_docnumber = JsonPointer('/exchange-document/@doc-number')
        pointer_kind = JsonPointer('/exchange-document/@kind')
        pointer_family_id = JsonPointer('/exchange-document/@family-id')

        pointer_application_reference = JsonPointer('/exchange-document/bibliographic-data/application-reference/document-id')
        pointer_publication_reference = JsonPointer('/exchange-document/bibliographic-data/publication-reference/document-id')
        pointer_invention_title = JsonPointer('/exchange-document/bibliographic-data/invention-title')
        pointer_abstract = JsonPointer('/exchange-document/abstract')
        pointer_applicant = JsonPointer('/exchange-document/bibliographic-data/parties/applicants/applicant')
        pointer_inventor = JsonPointer('/exchange-document/bibliographic-data/parties/inventors/inventor')


        pubref = pointer_publication_reference.resolve(data)
        self.publication_number_epodoc, self.publication_date = self.decode_document_number_date(pubref, 'epodoc')
        self.publication_number_docdb, _ = self.decode_document_number_date(pubref, 'docdb')

        appref = pointer_application_reference.resolve(data)
        self.application_number_epodoc, self.application_date = self.decode_document_number_date(appref, 'epodoc')
        self.application_number_docdb, _ = self.decode_document_number_date(pubref, 'docdb')

        try:
            titles = to_list(pointer_invention_title.resolve(data))
            title = self.decode_titles(titles)
        except JsonPointerException:
            title = {}

        try:
            abstracts = to_list(pointer_abstract.resolve(data))
            abstract = self.decode_abstracts(abstracts)
        except JsonPointerException:
            abstract = {}

        try:
            applicants = to_list(pointer_applicant.resolve(data))
            applicants = self.decode_parties(applicants, 'applicant-name')
        except JsonPointerException:
            applicants = []

        try:
            inventors = to_list(pointer_inventor.resolve(data))
            inventors = self.decode_parties(inventors, 'inventor-name')
        except JsonPointerException:
            inventors = []

        self.country = pointer_country.resolve(data)
        self.document_number = pointer_country.resolve(data) + pointer_docnumber.resolve(data) + pointer_kind.resolve(data)
        self.family_id = pointer_family_id.resolve(data)

        self.abstract = abstract
        self.title = title
        self.applicants = applicants
        self.inventors = inventors


class OPSRegisterDocument:
    """
    Implement the data model of OPS register documents.
    """

    def __init__(self):
        self.designated_states = []

    def read(self, data):

        designated_states_reference = JsonPointer('/reg:register-document/reg:bibliographic-data/reg:designation-of-states')
        self.designated_states = self.decode_designated_states(designated_states_reference.resolve(data))

    @staticmethod
    def decode_designated_states(data):
        """
        Decode designated states from register document.
        """

        countries_reference = JsonPointer('/reg:designation-pct/reg:regional/reg:country')
        countries_raw = to_list(countries_reference.resolve(data))

        states = []
        for country_raw in countries_raw:
            country = country_raw['$']
            states.append(country)

        return states
