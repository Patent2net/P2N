###################
Todo list and ideas
###################

******
Agenda
******

Improvements
============
Although Patent2Net is fully operational, works fine and is enough to begin using Patent Information, a lot can be done to improve analysis:

* Correct the issues (continuous process, of course)
* Add some more information in the result html page (ModeleContenuIndex.html). Great to add the treating date (thus can be different from gathering) and P2N version
* As information analysis do not allways represent the whole Patent Universe (i.e. french abstrat) provide the proportion of P.U. concerned by each analysis
* Treat Designated State(s) information for EP and WO patentes to complete the attractivity maps
* Improve the Mindmap option to get it more efficient for creativity (Celso is working on)
* Build the entire network as a gephi file for download to let new combined network analysis possible
* Use the list of standardised applicant names from EPO to normalize nets and tables. See: [CSV datafile] (http://documents.epo.org/projects/babylon/rawdata.nsf/0/71DE2EB24A084A19C1257F3B0032BA98/)


New capabilities
================
Add some new capabilities to Patent2Net, i.e.:

* Within the Patent Universe, build a drawings gallery with hyperlink to the Espacenet patent (Andre is working on)
* Within the Familly Patent Universe, provide all the same analysis as with the Patent Universe (Roberto is working on)
* Include the treatment of the Cooperative Patent Classification (CPC) with the proportion of P.U. concerned (http://www.cooperativepatentclassification.org/Archive.html)
* Build a small database to display results of a specific (Familly) Patent Universe. Database could be [PouchDB] (https://pouchdb.com/) or equivalent


New ways for gathering and analysis
===================================
Provide some new ways of gathering and analysis of patent information, i.e.:

* Within the Familly Patent Universe, provide a new range of analysis, considering a familly as a unique entity (invention)
* Limit the Familly Patent Universe to the only Priority patents, and provide a complete analysis
* Using citations of the Familly Patent Universe, provide genealogic analysis, especially descendants to try to detect invention fronts.
* Gather research reports when avalaible and provide analysis chains


New contributions and ideas are always welcome.


*****
Tasks
*****
- [x] Write about "jq"
- [o] Refactor maps.py and tables.py to ``p2n.formatters`` namespace
- [o] Write documentation about data model
- [o] Complete implementation of ``Patent2NetBrevet.from_ops_exchange_document`` re. citations, equivalents and more
- [o] Install Webhook on GitHub for automatic documentation building
- [o] Upload pre-release versions to PyPI
- [o] Resolve doc.designated_states vs. doc.register.designated_states duplication by providing a dotted name resolver for nested objects
