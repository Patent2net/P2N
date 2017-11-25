# -*- coding: utf-8 -*-
# (c) 2017 The Patent2Net Developers
import p2n.maps
import p2n.ops.client
from p2n.model import Patent2NetBrevet
from p2n.ops.client import OPSClient
from p2n.ops.model import OPSBiblioSearchResponse, OPSFamilyResponse


class Patent2Net:

    def __init__(self, ops_key, ops_secret):
        self.ops_key = ops_key
        self.ops_secret = ops_secret

        self.ops_client = OPSClient(self.ops_key, self.ops_secret)

        self.documents = []
        self.brevets = []

    def gather(self, expression, with_family=False):

        data = self.ops_client.search(expression)
        #print(json.dumps(data))
        response = OPSBiblioSearchResponse(data)

        self.documents = response.results

        if with_family:
            self.expand_family()

        self.documents_to_brevets()

        return self

    def expand_family(self):
        document_numbers = []
        documents_expanded = []
        for ops_exchange_document in self.documents:

            document_number = ops_exchange_document.publication_number

            document_numbers.append(document_number)
            documents_expanded.append(ops_exchange_document)

            #print 'document_number:', document_number
            #continue

            data = self.ops_client.family(document_number)
            response = OPSFamilyResponse(data)

            for family_member in response.results:

                # Skip family members which are the same as the document itself
                if family_member.publication_number == document_number:
                    continue

                #print 'family_member:', family_member.to_json(pretty=True)
                #print 'yeah'

                # Skip duplicates. Currently uses first-come, first-serve policy.
                if family_member.publication_number in document_numbers:
                    continue

                # Record expanded document
                document_numbers.append(family_member.publication_number)
                documents_expanded.append(family_member)

        self.documents = documents_expanded

    def documents_to_brevets(self):

        for ops_exchange_document in self.documents:

            # Create model instance of Patent2NetBrevet from OPSExchangeDocument
            brevet = Patent2NetBrevet.from_ops_exchange_document(ops_exchange_document)

            # Convert to dictionary in native P2N format
            p2n_brevet = brevet.as_dict()

            # Append to list of results
            self.brevets.append(p2n_brevet)

    def all(self):
        return self.brevets

    def worldmap(self, country_field):

        # Generate map data

        # FIXME: For "Applicant-Country" and "Inventor-Country",
        # this should actually count the number of unique items (name/country).
        # Currently, it counts just all countries, so the deviation is even greater
        # when running with "--with-family".

        mapdata = p2n.maps.d3plus_data(self.brevets, country_field)

        return mapdata
