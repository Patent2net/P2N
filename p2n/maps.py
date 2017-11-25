# -*- coding: utf-8 -*-
# (c) 2017 The Patent2Net Developers
import logging
import pkg_resources
from p2n.util import memoize

logger = logging.getLogger(__name__)

def d3plus_data(document_list, field):

    NomPays, NomTopoJSON = read_name_country_map()

    cptPay = dict()
    for document in document_list:

        if document[field] == '': continue
        country = document[field]

        if isinstance(country, list):
            for country in country:
                if country in NomPays.keys(): #aptent country in name (ouf)
                    if cptPay.has_key(NomPays[country]): #has it been found yet ?
                        cptPay[NomPays[country]] += 1 #so add one
                    else: #set it intead to one
                        cptPay[NomPays[country]] = 1
                elif country == 'SU':
                    if cptPay.has_key('RU'): #has it been found yet ?
                        cptPay[NomPays['RU']] += 1 #so add one
                    else: #set it intead to one
                        cptPay[NomPays['RU']] = 1
                else:
                    msg = 'Skipping country "{country}" for drawing on map, origin was "{label}".'.format(country=country, label=document['label'])
                    logger.info(msg)

        elif country in NomPays.keys(): #patent country in name (saved :-)
            if cptPay.has_key(NomPays[country]): #has it been found yet ?
                cptPay[NomPays[country]] += 1 #so add one
            else: #set it intead to one
                cptPay[NomPays[country]] = 1

        else:
            msg = 'Skipping country "{country}" for drawing on map, origin was "{label}".'.format(country=country, label=document['label'])
            logger.info(msg)

    mapdata = dict()
    for k in cptPay.keys():
        tempo = dict()
        tempo["value"] = cptPay[k]
        tempo["name"] = k
        tempo["country"] = NomTopoJSON[k]
        if "data" in mapdata.keys():
            mapdata["data"].append(tempo)
        else:
            mapdata["data"]=[tempo]

    return mapdata


@memoize
def read_name_country_map(filename=None):

    if not filename:
        filename = pkg_resources.resource_filename('p2n.resources', "NameCountryMap.csv")

    NomPays = dict()
    NomTopoJSON = dict()

    with open(filename, 'r') as fic:

        for line in fic.readlines():

            # Read line
            row = line.decode('utf-8').strip().split(';')

            # Decode row
            longcode = row[0]
            longname = row[1]
            countrycode = row[2].upper()

            # Assign to mapping dictionaries
            NomPays[countrycode] = longname
            NomTopoJSON[longname] = longcode

            # Using same dict for reverse mapping
            NomPays[longname] = countrycode

    return NomPays, NomTopoJSON
