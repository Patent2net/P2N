# -*- coding: utf-8 -*-
# (c) 2017 The Patent2Net Developers
import json
from pprint import pprint
import epo_ops
from epo_ops.models import Epodoc

class OPSClient:

    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret

        # Sanity checks
        # TODO

        # Create OPS client instance
        middlewares = [
            epo_ops.middlewares.Dogpile(),
            epo_ops.middlewares.Throttler(),
        ]
        self.client = epo_ops.Client(
            self.api_key, self.api_secret,
            accept_type='json', middlewares=middlewares)

    def search(self, expression):

        # Run data search and request bibliographic data for all results
        response = self.client.published_data_search(expression, constituents=['biblio'])
        #print(response.content)

        data = response.json()
        return data

    def crawl(self, expression):
        # TODO
        pass

    def family(self, document_number):
        response = self.client.family('publication', Epodoc(document_number), 'biblio')
        data = response.json()
        return data
