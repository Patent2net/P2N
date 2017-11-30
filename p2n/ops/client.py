# -*- coding: utf-8 -*-
# (c) 2017 The Patent2Net Developers
import logging
import epo_ops
from epo_ops.models import Epodoc

logger = logging.getLogger(__name__)


class OPSClient:

    def __init__(self, api_key, api_secret):

        self.api_key = api_key
        self.api_secret = api_secret

        # Sanity checks
        if not self.api_key or not self.api_secret:
            message = 'OPSClient needs OAuth credentials for accessing the OPS API'
            logger.error(message)
            raise ValueError(message)

        # Create OPS client instance
        middlewares = [
            epo_ops.middlewares.Dogpile(),
            epo_ops.middlewares.Throttler(),
        ]
        self.client = epo_ops.Client(
            self.api_key, self.api_secret,
            accept_type='json', middlewares=middlewares)

    def search(self, expression):
        """
        Run data search and request bibliographic data for all results
        """
        logger.info('Submitting search for expression "{}"'.format(expression))
        response = self.client.published_data_search(expression, constituents=['biblio'])
        data = response.json()
        return data

    def crawl(self, expression):
        # TODO
        pass

    def family(self, document_number):
        """
        Request family information for single document with number in epodoc format.
        """
        logger.info('Requesting family information for document "{}"'.format(document_number))
        response = self.client.family('publication', Epodoc(document_number), 'biblio')
        data = response.json()
        return data

    def register(self, document_number):
        """
        Request register information for single document with number in epodoc format.
        """
        logger.info('Requesting register information for document "{}"'.format(document_number))
        response = self.client.register('publication', Epodoc(document_number))
        data = response.json()
        return data
