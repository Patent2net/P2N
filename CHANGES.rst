##################
Patent2Net CHANGES
##################


development
===========

2017-11-30 3.0.0-dev1
=====================
- Minor fixes re. argument processing
- Improve robustness re. case-sensitivity at map resource acquisition (countries.json)
- Add setup.py, convenience step runner and documentation
- Refactor scripts "FormateExportAttractivityCartography.py" and "FormateExportCountryCartography.py"
- Use utility function for accessing cles-epo.txt
- Upgrade to python-epo-ops-client==2.3.1, fixing access to OPS API 3.2
- Make p2n.maps.d3plus_data obtain single field attribute
- Memoize outcome of p2n.maps.read_name_country_map
- Introduce ad-hoc mode
- Worldmap generation in ad-hoc mode is now based on native OPSExchangeDocument data model
- Enrich OPS bibliographic data by register information
- Add worldmap generation for designated states in ad-hoc mode
- Add automatic release task

2016-11-01 2.0.0
================
- Release Patent2Net 2.0.0
