# -*- coding: utf-8 -*-
"""
Created on 6/01/2017

@author: Luc, Andre
After loading patent list (created from OPSGather-BiblioPatent),
the script will proceed a check for each patent
if it is orphan or has a family. In the last case, family patents are added to
the initial list (may be some are already in it), and a hierarchic within
the priority patent (selected as the oldest representative) and its brothers is created.
IRAMUTEQ tagguing is added to analyse content
****PatentNumber ****date ****CIB3
"""

# BiblioProperties = ['publication-ref', 'priority-active-indicator', 'classification',
# u'resume', 'IPCR1', 'portee', 'IPCR3', 'applicant', 'IPCR4', 'IPCR7', 'label', 'IPCR11',
#'date', 'citations', 'application-ref', 'pays', u'abstract', 'titre', 'inventeur',
#'representative']

BiblioProperties = ['applicant', 'application-ref', 'citations', 'classification',
                    'prior-Date', 'prior-dateDate'
                    'inventor', 'IPCR1', 'IPCR11', 'IPCR3', 'IPCR4', 'IPCR7', 'label', 'country', 'kind',
                    'priority-active-indicator', 'title', 'date', "publication-ref", "representative",
                    "CPC", "prior", "priority-claim", "year", "family-id", "equivalent",
                    'inventor-country', 'applicant-country', 'inventor-nice', 'applicant-nice', 'CitP', 'CitO', 'references']
# from networkx_functs import *
import cPickle  # David? seems not used in this module

import os
import sys
import epo_ops
import json
from epo_ops.models import Docdb
from epo_ops.models import Epodoc
from P2N_Lib import ReturnBoolean, MakeIram2, LoadBiblioFile
from P2N_Config import LoadConfig


def download_image_meta(ops_client, patent_label, path_json):
    try:
        ans = ops_client.published_data(reference_type='publication',
                                        input=Epodoc(patent_label), endpoint='images')
        file(path_json, 'w').write(ans.content)
        return ans.json()
    except Exception as err:
        print "Image meta for {} error".format(patent_label), err


def extract_best_images(docs_instance):
    chosen_doc = None
    if isinstance(docs_instance, list):
        for doc in docs_instance:
            name = doc['@desc'].lower()
            if name == u'drawing':  # reset anything before and return this as better images results
                chosen_doc = doc
                break
            # elif name == u'fulldocument':
            #     chosen_doc = doc
            # elif name == u'firstpageclipping' and not chosen_doc:
            #     chosen_doc = doc
            # else:
            #     print 'Non recognized image doc instance', doc
    elif isinstance(docs_instance, dict) and docs_instance['@desc'].lower() == 'drawing':
        chosen_doc = docs_instance
    if not chosen_doc:
        return None, None, None
    link = chosen_doc[u'@link']
    page_start = int(chosen_doc[u'ops:document-section'][u'@start-page'])
    num_pages = int(chosen_doc[u'@number-of-pages'])
    return link, page_start, num_pages


def get_online_images(ops_client, path_image, link, page_start, num_pages):
    for page in range(page_start, page_start + num_pages):
        path_img = path_image.format(page)
        if not os.path.exists(path_img):
            print '... Retrieving img page {} of {}'.format(page, (page_start + num_pages - 1))
            resp = ops_client.image(link, range=page)
            file(path_img, 'w').write(resp.content)


os.environ['REQUESTS_CA_BUNDLE'] = 'cacert.pem'  # cacert.pem
os.environ['CA_BUNDLE'] = 'cacert.pem'

global key
global secret

# put your credential from epo client in this file...
# chargement clés de client
fic = open('../cles-epo.txt', 'r')
key, secret = fic.read().split(',')
key, secret = key.strip(), secret.strip()
fic.close()


DureeBrevet = 20
SchemeVersion = '20140101'  # for the url to the classification scheme

ListeBrevet = []  # The patent List


configFile = LoadConfig()
requete = configFile.requete
ndf = configFile.ndf
Gather = configFile.GatherContent
GatherBiblio = configFile.GatherBiblio
GatherPatent = configFile.GatherPatent
IsEnableScript = configFile.GatherImages

# should set a working dir one upon a time... done it is temporPath
ResultBiblioPath = configFile.ResultBiblioPath
ResultPathContent = configFile.ResultContentsPath
ResultPathImages = configFile.ResultPathImages
temporPath = configFile.temporPath
ResultAbstractPath = configFile.ResultAbstractPath

if IsEnableScript:
    ops_client = epo_ops.Client(key, secret)
    ops_client.accept_type = 'application/json'

    biblio_file = LoadBiblioFile(ResultBiblioPath, ndf)
    patents = biblio_file['brevets']

    for patent in patents:
        path_json = '{}//{}.json'.format(ResultPathImages, patent['label'])
        path_image = '{}//{}-{}.tiff'.format(ResultPathImages, patent['label'], '{}')
        js = None
        try:
            print "JSON image info for {} already gathered".format(patent['label'])
            js = json.load(file(path_json))
        except:
            js = download_image_meta(ops_client, patent['label'], path_json)
        docs_instance = js['ops:world-patent-data']['ops:document-inquiry']['ops:inquiry-result']['ops:document-instance']

        # try:
        link, page_start, num_pages = extract_best_images(docs_instance)
        if link:
            get_online_images(ops_client, path_image, link, page_start, num_pages)
        else:
            print 'Images for patent {} not found'.format(patent['label'])
        # except Exception as err:
        #     print "image for {} error".format(patent['label']), err
        #     import ipdb
        #     ipdb.set_trace()
