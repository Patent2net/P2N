# -*- coding: utf-8 -*-
# (c) 2017 The Patent2Net Developers
import re
import json
from collections import OrderedDict
from jsonpointer import JsonPointer, JsonPointerException
from p2n.util import to_list


class OPSBiblioSearchResponse:

    def __init__(self, data):
        self.data = data
        self.results = []
        self.read()

    def read(self):
        pointer_results = JsonPointer('/ops:world-patent-data/ops:biblio-search/ops:search-result/exchange-documents')
        exchange_documents = to_list(pointer_results.resolve(self.data))
        for exchange_document in exchange_documents:
            item = OPSExchangeDocument()
            item.read(exchange_document)
            self.results.append(item)


class OPSFamilyResponse:

    def __init__(self, data):
        self.data = data
        self.results = []
        self.read()

    def read(self):
        pointer_results = JsonPointer('/ops:world-patent-data/ops:patent-family/ops:family-member')
        family_members = to_list(pointer_results.resolve(self.data))
        for family_member in family_members:
            item = OPSExchangeDocument()
            try:
                item.read(family_member)
                self.results.append(item)
            except JsonPointerException:
                # FIXME
                pass


class OPSExchangeDocument:

    def __init__(self):
        self.application_date = None
        self.application_number = None
        self.publication_date = None
        self.publication_number = None
        self.title = {}
        self.abstract = None
        self.applicants = []
        self.inventors = []

    def to_json(self, pretty=False):
        if pretty:
            return json.dumps(self.__dict__, indent=4)
        else:
            return json.dumps(self.__dict__)

    @staticmethod
    def decode_document_number_date(docref, id_type):
        docref_list = to_list(docref)
        for document_id in docref_list:
            if document_id['@document-id-type'] == id_type:
                if id_type == 'epodoc':
                    doc_number = document_id['doc-number']['$']
                else:
                    doc_number = document_id['country']['$'] + document_id['doc-number']['$'] + document_id['kind']['$']
                date = document_id.get('date', {}).get('$')
                return doc_number, date
        return None, None

    @staticmethod
    def decode_titles(titles):
        data = OrderedDict()
        for title in titles:
            language = title.get(u'@lang', u'ol')
            value = title[u'$'] or u''
            if value:
                data[language] = value
        return data

    @staticmethod
    def decode_abstracts(abstracts):
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
        parties = []
        for party in partylist:

            if party['@data-format'] != 'epodoc':
                continue

            epodoc_name = party[name]['name']['$'].replace(u'\u2002', u' ')
            matches = re.match('(?P<name>.+?) \[(?P<country>.+?)\]', epodoc_name)
            if matches:
                parties.append(matches.groupdict())

        return parties

    def read(self, data):

        pointer_application_reference = JsonPointer('/exchange-document/bibliographic-data/application-reference/document-id')
        pointer_publication_reference = JsonPointer('/exchange-document/bibliographic-data/publication-reference/document-id')
        pointer_invention_title = JsonPointer('/exchange-document/bibliographic-data/invention-title')
        pointer_abstract = JsonPointer('/exchange-document/abstract')
        pointer_applicant = JsonPointer('/exchange-document/bibliographic-data/parties/applicants/applicant')
        pointer_inventor = JsonPointer('/exchange-document/bibliographic-data/parties/inventors/inventor')


        pubref = pointer_publication_reference.resolve(data)
        pubref_number, pubref_date = self.decode_document_number_date(pubref, 'epodoc')
        pubref_date = pubref_date and '-'.join([pubref_date[:4], pubref_date[4:6], pubref_date[6:8]])

        appref = pointer_application_reference.resolve(data)
        appref_number, appref_date = self.decode_document_number_date(appref, 'epodoc')
        appref_date = appref_date and '-'.join([appref_date[:4], appref_date[4:6], appref_date[6:8]])

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

        self.application_number = appref_number
        self.application_date = appref_date
        self.publication_number = pubref_number
        self.publication_date = pubref_date
        self.abstract = abstract
        self.title = title
        self.applicants = applicants
        self.inventors = inventors
