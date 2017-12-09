# -*- coding: utf-8 -*-
# (c) 2017 The Patent2Net Developers
import attr
import json
import logging
from collections import OrderedDict
from jsonpointer import JsonPointer, JsonPointerException
from p2n.ops.decoder import OPSExchangeDocumentDecoder
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
                publication_number, publication_date = OPSExchangeDocumentDecoder.document_number_date(document_id.resolve(family_member), 'epodoc')
            except JsonPointerException:
                pass

            # Read bibliographic data for family member
            item = OPSExchangeDocument()
            try:
                item.read(family_member)
                self.results.append(item)
            except JsonPointerException as ex:
                if "member 'exchange-document' not found" in ex.message:
                    logger.warning('No bibliographic data for family member "{}"'.format(publication_number))
                else:
                    raise


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


@attr.s
class OPSExchangeDocument(object):
    """
    Implement the data model of OPS exchange documents,
    optionally enriched by register information.
    """

    # Bibliographic data
    application_date = attr.ib(default=None)
    application_year = attr.ib(default=None)
    application_number_docdb = attr.ib(default=None)
    application_number_epodoc = attr.ib(default=None)

    publication_date = attr.ib(default=None)
    publication_year = attr.ib(default=None)
    publication_number_docdb = attr.ib(default=None)
    publication_number_epodoc = attr.ib(default=None)

    country = attr.ib(default=None)
    kind = attr.ib(default=None)
    document_number = attr.ib(default=None)
    family_id = attr.ib(default=None)

    title = attr.ib(default=attr.Factory(dict))
    abstract = attr.ib(default=attr.Factory(dict))

    classifications = attr.ib(default=attr.Factory(dict))
    applicants = attr.ib(default=attr.Factory(list))
    inventors = attr.ib(default=attr.Factory(list))

    # Register information
    register = attr.ib(default=None)


    # Infrastructure
    decoder = OPSExchangeDocumentDecoder


    def as_dict(self):
        return attr.asdict(self, dict_factory=OrderedDict)

    def to_json(self, pretty=False):
        """Convert document to JSON format"""
        if pretty:
            return json.dumps(self.as_dict(), indent=4)
        else:
            return json.dumps(self.as_dict())

    def read(self, data):
        """
        Read bibliographic information from raw OPS API JSON response.
        """

        #pprint(data)

        pubref = self.decoder.pointer_publication_reference.resolve(data)
        self.publication_number_epodoc, self.publication_date = self.decoder.document_number_date(pubref, 'epodoc')
        self.publication_number_docdb, _ = self.decoder.document_number_date(pubref, 'docdb')
        self.publication_year = self.publication_date[:4]

        appref = self.decoder.pointer_application_reference.resolve(data)
        self.application_number_epodoc, self.application_date = self.decoder.document_number_date(appref, 'epodoc')
        self.application_number_docdb, _ = self.decoder.document_number_date(appref, 'docdb')
        self.application_year = self.application_date[:4]

        self.applicants = self.decoder.applicants(data)
        self.inventors = self.decoder.inventors(data)

        self.country = self.decoder.pointer_country.resolve(data)
        self.kind = self.decoder.pointer_kind.resolve(data)
        self.document_number = self.country + self.decoder.pointer_docnumber.resolve(data) + self.kind
        self.family_id = self.decoder.pointer_family_id.resolve(data)

        self.abstract = self.decoder.abstracts(data)
        self.title = self.decoder.titles(data)

        self.classifications['IPC'] = self.decoder.classifications_ipc(data)
        self.classifications['IPCR'] = self.decoder.classifications_ipcr(data)
        self.classifications.update(self.decoder.classifications_more(data))


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
