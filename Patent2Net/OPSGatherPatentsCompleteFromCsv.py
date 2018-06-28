# -*- coding: utf-8 -*-
"""
Created on Tue Avr 1 13:41:21 2014

@author: dreymond
This script will load the request from file "requete.cql", construct the list
of patents corresponding to this request ans save it to the directorry ../DATA/PatentLists
Then, the bibliographic data associated to each patent in the patent List is collected and
stored to the same file name in the directory ../DATA/PatentBiblio.
"""

# BiblioPropertiesOLD = ['publication-ref', 'priority-active-indicator', 'classification',
#u'resume', 'IPCR1', 'portee', 'IPCR3', 'applicant', 'IPCR4', 'IPCR7', 'label', 'IPCR11',
#'date', 'citations', 'application-ref', 'pays', u'abstract', 'titre', 'inventeur',
#'representative', 'abs' ]
#
#
# BiblioPropertiesOLD2 =  ['applicant', 'application-ref', 'citations', 'classification',
#'inventor', 'IPCR1', 'IPCR11', 'IPCR3', 'IPCR4', 'IPCR7', 'label', 'country', 'kind',
#'priority-active-indicator', 'title','date',"publication-ref","representative",
#"CPC", "prior", "priority-claim", "year", "family-id", "equivalent",
# 'inventor-country', 'applicant-country', 'inventor-nice', 'applicant-nice']

# New in V2... 11/2015
BiblioProperties = ['applicant', 'application-ref', 'citations', 'classification',
                    'prior-Date', 'prior-dateDate'
                    'inventor', 'IPCR1', 'IPCR11', 'IPCR3', 'IPCR4', 'IPCR7', 'label', 'country', 'kind',
                    'priority-active-indicator', 'title', 'date', "publication-ref", "representative",
                    "CPC", "prior", "priority-claim", "year", "family-id", "equivalent",
                    'inventor-country', 'applicant-country', 'inventor-nice', 'applicant-nice', 'CitP', 'CitO', 'references']
#from networkx_functs import *
import cPickle
# from P2N_Lib import ExtractAbstract, ExtractClassificationSimple2, UniClean, SeparateCountryField, CleanPatent, ExtractPatent, ExtractPubliRefs,
from P2N_Lib import Initialize, PatentSearch,  GatherPatentsData, LoadBiblioFile
#from P2N_Lib import ProcessBiblio, MakeIram,  UnNest3, SearchEquiv, PatentCitersSearch
#from P2N_Lib import Update
#from P2N_Lib import EcritContenu, coupeEnMots
from P2N_Config import LoadConfig
from p2n.config import OPSCredentials

import epo_ops
import os
import sys
#from epo_ops.models import Docdb
#from epo_ops.models import Epodoc
os.environ['REQUESTS_CA_BUNDLE'] = 'cacert.pem'
global key
global secret

# put your credential from epo client in this file...
# chargement clés de client
c = OPSCredentials(credentials_file='../cles-epo.txt')
key, secret = c.read()

DureeBrevet = 20
SchemeVersion = '20140101'  # for the url to the classification scheme
import os

ListeBrevet = []  # LA iste de brevets
# ouverture fichier de travail

ficOk = False
cptNotFound = 0
nbTrouves = 0

lstBrevets = []  # The patent List
BiblioPatents = []  # The bibliographic data


configFile = LoadConfig()
requete = configFile.requete
ndf = configFile.ndf
GatherBiblio = configFile.GatherBiblio
GatherBibli = configFile.GatherBiblio
GatherPatent = configFile.GatherPatent
GatherFamilly = configFile.GatherFamilly

# should set a working dir one upon a time... done it is temporPath
ResultListPath = configFile.ResultListPath
ResultBiblioPath = configFile.ResultBiblioPath
ResultContentsPath = configFile.ResultContentsPath
temporPath = configFile.temporPath
ResultAbstractPath = configFile.ResultAbstractPath

def OpenCsv(csvFile):
    with open(csvFile, 'r') as fic:
        data=fic.read()
    pat, kind = [], []
    data = data.split('\n')
    for lig in data:
        if len(lig)>0 and ';' in lig:
            temp = lig.split(';')
            pat.append(temp[0])
            tempo = temp[1]
            tempo = tempo.replace("(", "")
            tempo = tempo.replace(")", "")
            kind.append(tempo)
        else:
            print lig
    return pat, kind
# by default, data are not gathered yet
# building patentList
nbTrouves = 0
# if GatherPatent:
BiblioPatents, PatIgnored = [], Initialize(GatherPatent, GatherBiblio)

ops_client = epo_ops.Client(key, secret)
#        data = ops_client.family('publication', , 'biblio')
ops_client.accept_type = 'application/json'
GatherBibli = GatherBiblio  # this parametric option was added after...

with open(ResultListPath + '//' + ndf, 'r') as fic:
        DataBrevets = cPickle.load(fic)
        lstBrevets = DataBrevets['brevets']
        nbActus = DataBrevets['number']

STOP = False

PatToFind, AssociatedKind = OpenCsv('HD.csv')


    
# else:
#
#    print "Good, nothing to do"

listeLabel = []
for brevet in lstBrevets:
    if u'document-id' in brevet.keys() and "invalid result" not in str(brevet):
        # nameOfPatent for file system save (abstract, claims...)
        ndb = brevet[u'document-id'][u'country']['$'] + brevet[u'document-id'][u'doc-number']['$']
        listeLabel.append(ndb)
print "Found almost", len(lstBrevets), " patents. Saving list"
print "Within ", len(set(listeLabel)), " unique patents"

listeLab = list(set(PatToFind))
 
#for lab in listeLab: #☻from scratch
#    temp,  nbTrouves = PatentSearch(ops_client, "pn="+lab,1, 1)
#    for p in temp:
#        if p not in lstBrevets:
#                lstBrevets.append(p)
#                ajouts += 1
# Entering PatentBiblio feeding
print "Gathering bibliographic data " 
if GatherBibli and GatherBiblio:
    DataBrevets = dict()
    DataBrevets['brevets'] = []
    if ndf in os.listdir(ResultBiblioPath):
        with open(ResultBiblioPath + '//' + ndf, 'r') as fic:
            while 1:
                try:
                    DataBrevets['brevets'].append(cPickle.load(fic))
                except EOFError:
                    break

            if len(DataBrevets['brevets']) == len(listeLabel):
                print len(DataBrevets['brevets']), " bibliographic patent data gathered yet? Nothing else to do :-)"
                GatherBibli = False
                for brevet in lstBrevets:
                    # nameOfPatent for file system save (abstract, claims...)
                    ndb = brevet[u'document-id'][u'country']['$'] + \
                        brevet[u'document-id'][u'doc-number']['$']
                    listeLabel.append(ndb)
    else:
        ficOk = False
        print str(abs(len(lstBrevets) - len(DataBrevets['brevets']))), " patents data missing. Gathering."
        GatherBibli = True

PatIgnored = 0


if GatherBibli and GatherBiblio:
    ops_client = epo_ops.Client(key, secret)
    #        data = ops_client.family('publication', , 'biblio')
    ops_client.accept_type = 'application/json'
    if "brevets" in DataBrevets.keys():
        YetGathered = list(set([bre['label'] for bre in DataBrevets["brevets"]]))
        print len(YetGathered), " patent bibliographic data gathered."
        DataBrevets["YetGathered"] = YetGathered
    elif "YetGathered" in DataBrevets.keys():
        YetGathered = DataBrevets["YetGathered"]
    else:
        YetGathered = []
    import datetime
    toGather = [(listeLab[indice], AssociatedKind[indice]) for indice in range(len(listeLab)) if listeLab[indice] not in YetGathered] + \
    [truc for truc in lstBrevets if truc[u'document-id'][u'country']['$'] + truc['document-id'][u'doc-number']['$'] not in YetGathered]
    
    
    for brevet in toGather:
        #if 'invalid result' not in str(brevet) and u'document-id' in brevet.keys():
            # nameOfPatent for file system save (abstract, claims...)
            listeLabel.append(ndb)
            
            BiblioPatents = GatherPatentsData( brevet, ops_client, ResultContentsPath, ResultAbstractPath,  PatIgnored, [])
    # may be current patent has already be gathered in a previous attempt
    # should add a condition here to check in os.listdir()
#            except:
#                print ndb, " ignored... error occured"
#                next
            if BiblioPatents is None:
                BiblioPatents = []
            tempor = []
            for pat in BiblioPatents:
                if "year" not in pat.keys():  # something didn't go well... Forcing
                    if 'date' not in pat.keys() and 'prior-Date' not in pat.keys() and 'dateDate' not in pat.keys() and 'prior-dateDate' not in pat.keys():
                        pat['date'] = ['1-1-1']
                        pat['prior-Date'] = [u'1-1-1']
                        pat['dateDate'] = datetime.date(1, 1, 1)
                        pat['prior-dateDate'] = datetime.date(1, 1, 1)
                        pat['year'] = ['1']
                    elif 'date' not in pat.keys() and 'prior-Date' not in pat.keys() and 'dateDate' not in pat.keys():
                        if isinstance(pat['prior-dateDate'], list) and len(pat['prior-dateDate']) == 1:
                            if pat['prior-dateDate'][0].year > 1:
                                pat['date'] = [str(pat['prior-dateDate'][0].year) + '-' + str(
                                    pat['prior-dateDate'][0].month) + '-' + str(pat['prior-dateDate'][0].day)]
                                pat['prior-Date'] = pat['date']
                                pat['dateDate'] = pat['prior-dateDate'][0]
                                pat['year'] = [str(pat['prior-dateDate'][0].year)]
                            else:
                                pat['date'] = ['1-1-1']
                                pat['prior-Date'] = [u'1-1-1']
                                pat['dateDate'] = datetime.date(1, 1, 1)
                                pat['prior-dateDate'] = datetime.date(1, 1, 1)
                                pat['year'] = ['1']
                        else:  # booring cases, forcing a little hereafter... many case will be good, others less.... need developper here !
                            pat['date'] = ['1-1-1']
                            pat['prior-Date'] = [u'1-1-1']
                            pat['dateDate'] = datetime.date(1, 1, 1)
                            pat['prior-dateDate'] = datetime.date(1, 1, 1)
                            pat['year'] = ['1']

                    elif 'dateDate' not in pat.keys():
                        pat['date'] = ['1-1-1']
                        pat['prior-Date'] = [u'1-1-1']
                        pat['dateDate'] = datetime.date(1, 1, 1)
                        pat['prior-dateDate'] = datetime.date(1, 1, 1)
                        pat['year'] = ['1']

                    else:
                        pat['date'] = ['1-1-1']
                        pat['prior-Date'] = [u'1-1-1']
                        pat['dateDate'] = datetime.date(1, 1, 1)
                        pat['prior-dateDate'] = datetime.date(1, 1, 1)
                        pat['year'] = ['1']

                tempor.append(pat)
            BiblioPatents = tempor
            if BiblioPatents is not None and BiblioPatents != []:
                with open(ResultBiblioPath + '//' + ndf, 'a') as ficRes:
                    cPickle.dump(BiblioPatents[0], ficRes)
                    YetGathered.append(BiblioPatents[0]["label"])
                    print len(YetGathered), " patent bibliographic data already gathered."
            else:
                # may should put current ndb in YetGathered...
                # print
                pass
    #
    with open(ResultBiblioPath + '//Description' + ndf, 'w') as ficRes:
        DataBrevets['ficBrevets'] = ndf
        DataBrevets['requete'] = requete
        DataBrevets["YetGathered"] = YetGathered
        DataBrevets.pop("brevets")
        cPickle.dump(DataBrevets, ficRes)

    NotGathered = [pat for pat in listeLabel if pat not in YetGathered]
    print "Ignored  patents from patent list", PatIgnored
    print "unconsistent patents: ", len(NotGathered)
    print "here is the list: ", " DATA\PatentContentHTML\\" + ndf

    print "Export in HTML using FormateExport"
#os.system("FormateExport.exe "+ndf)
#os.system("CartographyCountry.exe "+ndf)
