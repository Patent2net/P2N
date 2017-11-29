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
#u'resume', 'IPCR1', 'portee', 'IPCR3', 'applicant', 'IPCR4', 'IPCR7', 'label', 'IPCR11',
#'date', 'citations', 'application-ref', 'pays', u'abstract', 'titre', 'inventeur',
#'representative']

BiblioProperties = ['applicant', 'application-ref', 'citations', 'classification',
                    'prior-Date', 'prior-dateDate'
                    'inventor', 'IPCR1', 'IPCR11', 'IPCR3', 'IPCR4', 'IPCR7', 'label', 'country', 'kind',
                    'priority-active-indicator', 'title', 'date', "publication-ref", "representative",
                    "CPC", "prior", "priority-claim", "year", "family-id", "equivalent",
                    'inventor-country', 'applicant-country', 'inventor-nice', 'applicant-nice', 'CitP', 'CitO', 'references']
#from networkx_functs import *
import cPickle  # David? seems not used in this module

import os
import sys
import epo_ops
from epo_ops.models import Docdb
from epo_ops.models import Epodoc
from P2N_Lib import ReturnBoolean, MakeIram2, LoadBiblioFile
from P2N_Config import LoadConfig

# David? produce an error in Spyder : ImportError: No module named P2N_Lib


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
        path = '{}//{}.tiff'.format(ResultPathImages,  patent['label'])
        if os.path.exists(path):
            print "Image for {} already gathered".format(patent['label'])
        else:
            try:
                ans = ops_client.published_data(reference_type='publication',
                                                input=Epodoc(patent['label']), endpoint='images')
                j = ans.json()
                base_u = j['ops:world-patent-data']['ops:document-inquiry']['ops:inquiry-result']['ops:document-instance'][0]['@link']
                resp = ops_client.image(base_u)
                file(path, 'w').write(resp.content)
            except Exception as err:
                print "image for {} error".format(patent['label']), err
