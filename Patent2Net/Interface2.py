# -*- coding: utf-8 -*-
"""
Created on Sun Feb 15 09:12:25 2015

@author: dreymond
"""

from P2N_Lib import LoadBiblioFile, RenderTemplate
from P2N_Config import LoadConfig
import codecs
import os
import cPickle
nbFam = 0

configFile = LoadConfig()
requete = configFile.requete
ndf = configFile.ndf
Gather = configFile.GatherContent
GatherBiblio = configFile.GatherBiblio
GatherPatent = configFile.GatherPatent
GatherFamilly = configFile.GatherFamilly
P2NInv = configFile.InventorNetwork
AppP2N = configFile.ApplicantNetwork
P2NAppInv = configFile.ApplicantInventorNetwork
P2NInvCT = configFile.InventorCrossTechNetwork
P2NComp = configFile.CompleteNetwork
P2NCountryCT = configFile.CountryCrossTechNetwork
P2NFamilly = configFile.FamiliesNetwork
P2NHieracFamilly = configFile.FamiliesHierarchicNetwork

 #should set a working dir one upon a time... done it is temporPath
ResultBiblioPath = configFile.ResultBiblioPath
ResultPatentPath = configFile.ResultListPath
ResultContentsPath = configFile.ResultContentsPath

GlobalPath = configFile.GlobalPath

# take request from BiblioPatent file


if 'Description'+ndf in os.listdir(ResultBiblioPath): # NEW 12/12/15 new gatherer append data to pickle file in order to consume less memory
    data = LoadBiblioFile(ResultBiblioPath, ndf)
    requete = data['requete']
else: #Retrocompatibility
    print "please use Comptatibilizer"
    #if 'Fusion' in data.keys()
    data = dict()
if GatherFamilly:#pdate needed for families
    if 'DescriptionFamilies'+ndf in os.listdir(ResultBiblioPath): # NEW 12/12/15 new gatherer append data to pickle file in order to consume less memory
        data2 = LoadBiblioFile(ResultBiblioPath, 'Families' + ndf)
        nbFam = len(data2['brevets'])
    else: #Retrocompatibility
        print "please use Comptatibilizer"
    #if 'Fusion' in data.keys()with open( ResultBiblioPath+'//Families'+ndf, 'r') as ficBib:
 #        data2 = cPickle.load(ficBib)

else:
    nbFam=0

import datetime
today = datetime.datetime.today()
date = today.strftime('%d, %b %Y')

totalPatents = ""
if data.has_key("brevets"): #compatibility, this may be useless
    totalPatents = len(data["brevets"])
else:
    totalPatents = "see datatable :-)"

# new method to count documents by type
totalsPerType = {}
if Gather:
    for content in [u'Abstract', u'Claims', u'Description', u'FamiliesAbstract', u'FamiliesClaims', u'FamiliesDescription' ]:
        path = ResultContentsPath + content
        if os.path.isdir(path):
            lstfic = os.listdir(path)
            languages = set([str(fi[0:2]) for fi in lstfic])
            totalsPerType[content] = {
                "total": len(lstfic),
                "languages": ", ".join(languages)
            }


RenderTemplate(
    "ModeleContenuIndex.html",
    GlobalPath+'//'+ndf+'.html',
    CollectName=ndf,
    Request=requete,
    TotalPatents=totalPatents,
    TotalFamily=nbFam,
    HasFamily=GatherFamilly,
    Date=date,
    TotalsPerType=totalsPerType,


)

# updating index.js for server side and local menu
inFile =[] # memorize content
with open('../dex.js') as FicRes:
    data = FicRes.readlines()
    for lig in data[2:]:
        if '</ul>' not in lig and "');" not in lig:
            inFile.append(lig)

with open('../dex.js', 'w') as ficRes:
    ficRes.write("document.write('\ ".strip())
    ficRes.write("\n")
    ficRes.write(" <ul>\ ".strip())
    ficRes.write("\n")

     # write last analyse
    ficRes.write("""<li><a href="DATA/***request***.html" target="_blank">***request***</a></li>\ """.replace('***request***', ndf).strip())
    ficRes.write("\n")
    for exist in inFile:
        if ndf not in exist:
            ficRes.write(exist.strip().replace('</ul>\ ', ''))
            ficRes.write("\n")

    ficRes.write(" </ul>\ ".strip())
    ficRes.write("\n")
    ficRes.write("');")
