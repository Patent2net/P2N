# -*- coding: utf-8 -*-
"""
Created on Thu Feb 05 16:27:36 2015

@author: dreymond

Draws the map of patent deposit for a universe.
Next version should consider EP and WO patents
"""


import json
import os
import cPickle
#from bs4.dammit import EntitySubstitutions
from P2N_Lib import LoadBiblioFile, RenderTemplate
from P2N_Config import LoadConfig

configFile = LoadConfig()
requete = configFile.requete
Gather = configFile.GatherContent
GatherBiblio = configFile.GatherBiblio
GatherPatent = configFile.GatherPatent
IsEnableScript = configFile.FormateExportCountryCartography
P2NFamilly = configFile.GatherFamilly

 #should set a working dir one upon a time... done it is temporPath
ResultListPath = configFile.ResultListPath
ListBiblioPath = configFile.ResultBiblioPath
temporPath = configFile.temporPath
ResultPathContent = configFile.ResultPath

if IsEnableScript:
    prefixes = [""]
    if P2NFamilly:
        prefixes.append("Families")

    for prefix in prefixes:
        ndf = prefix + configFile.ndf

        #if ndf.count('Families')>0:
        #    clesRef = ['label',  'titre', 'date', 'citations','family lenght', 'priority-active-indicator', 'classification', 'portee', 'applicant', 'pays', 'inventeur', 'representative', 'prior']
        #else:
        # the list of keys in database
        clesRef = ['label', 'title', 'year','priority-active-indicator',
        'IPCR11', 'kind', 'applicant', 'country', 'inventor', 'representative', 'IPCR4',
        'IPCR7', "Inventor-Country", "Applicant-Country", "equivalents", "CPC", u'references', u'Citations', u'CitedBy']


        print "\n> Hi! This is CountryCartography formatter. "
        if 'Description'+ndf in os.listdir(ListBiblioPath): # NEW 12/12/15 new gatherer append data to pickle file in order to consume less memory
            LstBrevet = LoadBiblioFile(ListBiblioPath, ndf)
            with open(ListBiblioPath +'//Description'+ndf, 'r') as ficRes:
                DataBrevet = cPickle.load(ficRes)
        else: #Retrocompatibility
            with open(ListBiblioPath+'//'+ndf, 'r') as data:
                LstBrevet = cPickle.load(data)
            with open(ResultListPath+'//'+ndf, 'r') as data:
                DataBrevet = cPickle.load(data)
                ##next may need clarifying update
        if isinstance(LstBrevet, dict):
            data = LstBrevet
            LstBrevet = data['brevets']
            if data.has_key('requete'):
                DataBrevet['requete'] = data["requete"]
            if "requete" not in DataBrevet.keys():
                DataBrevet['requete'] = "?"
            if data.has_key('number'):
                print "Found ", data["number"], " patents! Formating to HMTL Cartography (Beta)"

        NomPays = dict()
        NomTopoJSON = dict()
        #list value in countries, avoiding
        for bre in LstBrevet:
            if isinstance(bre['country'], list) and len(bre['country'])==1:
                bre['country'] = bre['country'][0] # well, taking the first one, this is an approximation
        print "mapping ", len(LstBrevet), "patents. Excepting EP and WO"

        with open('NameCountryMap.csv', 'r') as fic:
            #2 means using short name...
            for lig in fic.readlines():
                li = lig.strip().split(';')
                NomPays[li[2].upper()] = li[1]
                NomTopoJSON[li[1]] = li[0]
                NomPays[li[1]] = li[2].upper() #using same dict for reverse mapping
        cptPay = dict()
        for bre in LstBrevet:
            if bre['country'] in NomPays.keys(): #aptent country in name (ouf)
                if cptPay.has_key(NomPays[bre['country']]): #has it been found yet ?
                    cptPay[NomPays[bre['country']]] += 1 #so add one
                else: #set it intead to one
                    cptPay[NomPays[bre['country']]] = 1
            else:
                if bre['country'] not in ['EP', 'WO']:
                    print  bre['country']
        dico =dict()
        for k in cptPay.keys():
            tempo = dict()
            tempo["value"] = cptPay[k]
            tempo["name"] = k
            tempo["country"] = NomTopoJSON[k]
            if "data" in dico.keys():
                dico["data"].append(tempo)
            else:
                dico["data"]=[tempo]
        with open(ResultPathContent+'//'+ndf+"CountryMap.json", "w") as fic:
            json.dump(dico, fic)
            resJsonName = ndf+"CountryMap.json"

        RenderTemplate(
            "ModeleCarto.html",
            ResultPathContent + '//' + ndf+'Carto.html',
            jsonFile=resJsonName,
            request=requete.replace('"', ''),
        )

        #due to limit of D3, countries ressources are necessary placed
        # in same working directory... other solution is to start an http server
        # http://stackoverflow.com/questions/17077931/d3-samples-in-a-microsoft-stack

        with open(ResultPathContent+'//' + prefix + 'Countries.json', "w") as fic:
            with open('countries.json', 'r') as fic2:
                tempo = fic2.read()
                fic.write(tempo)
