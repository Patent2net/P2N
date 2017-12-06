# -*- coding: utf-8 -*-
# (c) 2017 The Patent2Net Developers
import attr
from collections import OrderedDict
from Patent2Net.P2N_Lib import NiceName


@attr.s
class Patent2NetBrevet(object):

    label = attr.ib(default='')
    country = attr.ib(default='')
    kind = attr.ib(default='')
    date = attr.ib(default='')
    year = attr.ib(default='')

    title = attr.ib(default='')

    applicant = attr.ib(default=attr.Factory(list))
    applicant_nice = attr.ib(default='')
    application_ref = attr.ib(default='')

    inventor = attr.ib(default=attr.Factory(list))
    inventor_nice = attr.ib(default='')

    Applicant_Country = attr.ib(default='')
    Inventor_Country = attr.ib(default='')

    equivalents = attr.ib(default=attr.Factory(list))
    family_length = attr.ib(default=0)

    classification = attr.ib(default=attr.Factory(list))
    CPC = attr.ib(default=attr.Factory(list))
    IPCR1 = attr.ib(default='')
    IPCR11 = attr.ib(default='')
    IPCR3 = attr.ib(default=attr.Factory(list))
    IPCR4 = attr.ib(default=attr.Factory(list))
    IPCR7 = attr.ib(default=attr.Factory(list))

    CitO = attr.ib(default='')
    CitP = attr.ib(default=attr.Factory(list))
    Citations = attr.ib(default=0)
    CitedBy = attr.ib(default='')

    prior = attr.ib(default='')
    prior_date = attr.ib(default='')
    priority_active_indicator = attr.ib(default='')

    references = attr.ib(default=0)
    representative = attr.ib(default=0)

    designated_states = attr.ib(default=attr.Factory(list))

    @classmethod
    def from_ops_exchange_document(cls, document):

        brevet = cls()

        brevet.country = document.country
        brevet.kind = document.kind
        brevet.label = document.publication_number_epodoc

        brevet.date = document.publication_date
        brevet.year = document.publication_year

        brevet.applicant = [item['name'] for item in document.applicants]
        brevet.inventor = [item['name'] for item in document.inventors]
        brevet.applicant_nice = NiceName(brevet.applicant)
        brevet.inventor_nice = NiceName(brevet.inventor)

        if document.classifications and document.classifications['IPCR']:
            ipcr_classes = document.classifications['IPCR']
            brevet.classification = ipcr_classes

            brevet.IPCR1 = list(set([ipcr[0] for ipcr in ipcr_classes]))
            brevet.IPCR3 = list(set([ipcr[:3] for ipcr in ipcr_classes]))
            brevet.IPCR4 = list(set([ipcr[:4] for ipcr in ipcr_classes]))
            brevet.IPCR7 = list(set([ipcr.split('/')[0] for ipcr in ipcr_classes]))


        if document.applicants:
            brevet.Applicant_Country = document.applicants[0]['country']

        if document.inventors:
            brevet.Inventor_Country = document.inventors[0]['country']

        if document.register:
            brevet.designated_states = document.register.designated_states

        return brevet

    def as_dict(self):

        """
        Blueprint:

        {
        'Applicant-Country': '',
        'CPC': ['B29D11/00932',
                'B24B9/142',
                'Y10T29/49995',
                'Y10T29/49996'],
        'CitO': '',
        'CitP': ['US3030859',
                 'US3078560',
                 'US3145506',
                 'US3160039',
                 'US3301105',
                 'US3423886',
                 'US3528326'],
        'Citations': 0,
        'CitedBy': '',
        'IPCR1': 'B',
        'IPCR11': 'B24B9/14',
        'IPCR3': ['B24', 'B29'],
        'IPCR4': ['B24B', 'B29D'],
        'IPCR7': ['B24B9', 'B29D11'],
        'Inventor-Country': '',
        'applicant': 'ESSILOR INT',
        'applicant-nice': 'EssilorInt',
        'application-ref': 1.0,
        'classification': ['B24B9/14', 'B29D11/00'],
        'country': 'US',
        'date': '1973-08-07',
        'dateDate': datetime.date(1973, 8, 7),
        'equivalents': ['NL7100827',
                        'CH528964',
                        'GB1343301',
                        'DE2102820',
                        'CA931760',
                        'BE761834',
                        'US3750272',
                        'FR2076643',
                        'JPS5613583B'],
        'family lenght': 11,
        'inventor': 'GOMOND G',
        'inventor-nice': 'GomondG',
        'kind': 'A',
        'label': 'US3750272',
        'prior': 'BE761834',
        'prior-Date': '1970-01-22',
        'prior-dateDate': datetime.date(1970, 1, 22),
        'priority-active-indicator': 1,
        'references': 7,
        'representative': 0,
        'title': 'MACHINING CONTACT LENSES OF FLEXIBLE MATERIAL',
        'year': '1973'
        }
        """

        fields = attr.fields(Patent2NetBrevet)
        fieldnames = [field.name for field in fields]
        #print 'fieldnames:', fieldnames

        result = OrderedDict()
        for key in fieldnames:

            value = getattr(self, key)
            key = key.replace('family_length', 'family lenght')
            key = key.replace('_', '-')

            result[key] = value

        return result
