# -*- coding: utf-8 -*-
# (c) 2017 The Patent2Net Developers
import re
import logging
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
                date = date and '-'.join([date[:4], date[4:6], date[6:8]])
                return doc_number, date
        return None, None

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

        entries = to_list(cls.pointer_ipcr.resolve(data))

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
