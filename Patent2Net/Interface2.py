# -*- coding: utf-8 -*-
"""
Created on Sun Feb 15 09:12:25 2015

@author: dreymond
"""

from P2N_Lib import ReturnBoolean, LoadBiblioFile, RenderTemplate
import codecs
import os
import cPickle
nbFam = 0
with open("..//requete.cql", "r") as fic:
    contenu = fic.readlines()
    for lig in contenu:
        #if not lig.startswith('#'):
            if lig.count('request:')>0:
                requete=lig.split(':')[1].strip()
            if lig.count('DataDirectory:')>0:
                ndf = lig.split(':')[1].strip()
            if lig.count('GatherContent')>0:
                Gather = ReturnBoolean(lig.split(':')[1].strip())
            if lig.count('GatherBiblio')>0:
                GatherBiblio = ReturnBoolean(lig.split(':')[1].strip())
            if lig.count('GatherPatent')>0:
                GatherPatent = ReturnBoolean(lig.split(':')[1].strip())
            if lig.count('GatherFamilly')>0:
                GatherFamilly = ReturnBoolean(lig.split(':')[1].strip())
            if lig.count('InventorNetwork')>0:
                P2NInv = ReturnBoolean(lig.split(':')[1].strip())
            if lig.count('ApplicantNetwork')>0:
                AppP2N = ReturnBoolean(lig.split(':')[1].strip())
            if lig.count('ApplicantInventorNetwork')>0:
                P2NAppInv = ReturnBoolean(lig.split(':')[1].strip())
            if lig.count('InventorCrossTechNetwork')>0:
                P2NInvCT = ReturnBoolean(lig.split(':')[1].strip())
            if lig.count('CompleteNetwork')>0:
                P2NComp = ReturnBoolean(lig.split(':')[1].strip())
            if lig.count('CountryCrossTechNetwork')>0:
                P2NCountryCT = ReturnBoolean(lig.split(':')[1].strip())
            if lig.count('FamiliesNetwork')>0:
                P2NFamilly = ReturnBoolean(lig.split(':')[1].strip())
            if lig.count('FamiliesHierarchicNetwork')>0:
                P2NHieracFamilly = ReturnBoolean(lig.split(':')[1].strip())

GlobalPath ='..//DATA'
ResultPath = GlobalPath+'//'+ndf+'//PatentBiblios'
ResultPatentPath = GlobalPath+'//'+ndf+'//PatentLists'

ResultPathGephi = GlobalPath+'//'+ndf+'//GephiFiles'
ResultPathContent = GlobalPath+'//'+ndf

# take request from BiblioPatent file


if 'Description'+ndf in os.listdir(ResultPath): # NEW 12/12/15 new gatherer append data to pickle file in order to consume less memory
    data = LoadBiblioFile(ResultPath, ndf)
    requete = data['requete']
else: #Retrocompatibility
    print "please use Comptatibilizer"
    #if 'Fusion' in data.keys()
    data = dict()
if GatherFamilly:#pdate needed for families
    if 'DescriptionFamilies'+ndf in os.listdir(ResultPath): # NEW 12/12/15 new gatherer append data to pickle file in order to consume less memory
        data2 = LoadBiblioFile(ResultPath, 'Families' + ndf)
        nbFam = len(data2['brevets'])
    else: #Retrocompatibility
        print "please use Comptatibilizer"
    #if 'Fusion' in data.keys()with open( ResultPath+'//Families'+ndf, 'r') as ficBib:
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
        path = ResultPathContent+'//PatentContents//' + content
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






#
#
# ficRes = codecs.open(GlobalPath+'//'+ndf+'.html', 'w', 'utf8')
#
# with codecs.open('ModeleContenuIndex.html', 'r', 'utf8') as fic:
#     NouveauContenu = fic.read()
#
#
# with open('ModeleIndexRequete.html', 'r') as fic:
#     html = fic.read()
#     html = html[:html.index('</body>')]
# html  = html .replace("***Request***", requete)
#
#
#
#
#
# html += NouveauContenu + """
#   </body>
# </html>
# """
# ficRes.write(html)
# ficRes.close()

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
