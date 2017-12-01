#####
Usage
#####

.. contents::
   :local:
   :depth: 1

----

*****************
Classic interface
*****************

Create a .cql file
==================
Copy one of the \*.cql files from the ``/RequestsSets`` directory as ``requete.cql``
to the root directory and adapt this file to your needs.

Run suite of scripts
====================
Use the ``/Patent2Net/ProcessPy.bat`` or the ``/Patent2Net/Process.sh`` file and enjoy!
Please also have a look at the `query howto`_ about how to formulate a query expression.

.. _query howto: http://patent2netv2.vlab4u.info/dokuwiki/doku.php?id=user_manual:patent_search

----


****************
Modern interface
****************
The modern interface allows to specify a ``requete.cql`` file on the command line
or by using the environment variable ``P2N_CONFIG``.


Acquire data from OPS
=====================
Run Patent2Net::

    p2n acquire --config=/path/to/RequestsSets/Lentille.cql

Alternatively, you can specify the path to the ``requete.cql`` using an environment variable::

    export P2N_CONFIG=`pwd`/RequestsSets/Lentille.cql

then, just run::

    # Acquire patent information from OPS
    p2n acquire

    # Also acquire family information for each hit
    p2n acquire --with-family


Analyze information
===================
When running the analysis commands like this, you should set
the ``P2N_CONFIG`` environment variable for convenience, like described above.

E.g., run::

    # Build all world maps
    p2n maps

    # Build all network graphs
    p2n networks

    # p2n {maps,networks,tables,bibfile,iramuteq,freeplane,carrot}
    # see full list below or run ``p2n --help``

----


****************
Ad-hoc interface
****************
The ad-hoc interface allows to specify the query expression on the command line
and uses a different acquisition machinery under the hood.
Through caching, multiple invocations will still be fast.

Display list of publication numbers for given query expression::

    p2n adhoc list --expression='TA=lentille'
    p2n adhoc list --expression='TA=lentille' --with-family

Display bibliographic data for given query expression in Patent2NetBrevet format::

    p2n adhoc dump --expression='TA=lentille'

Generate data for world maps using d3plus/geo_map (JSON)::

    p2n adhoc worldmap --expression='TA=lentille' --country-field='country'
    p2n adhoc worldmap --expression='TA=lentille' --country-field='country' --with-family
    p2n adhoc worldmap --expression='TA=lentille' --country-field='applicants'
    p2n adhoc worldmap --expression='TA=lentille' --country-field='inventors'
    p2n adhoc worldmap --expression='TA=lentille' --country-field='designated_states' --with-register


----


********
Synopsis
********

Full output of "``p2n --help``"
===============================
::

    $ p2n --help

    Usage:
      p2n ops init --key=<ops-oauth-key> --secret=<ops-oauth-secret>
      p2n acquire [--config=requete.cql] [--with-family]
      p2n maps [--config=requete.cql]
      p2n networks [--config=requete.cql]
      p2n tables [--config=requete.cql]
      p2n bibfile [--config=requete.cql]
      p2n iramuteq [--config=requete.cql]
      p2n freeplane [--config=requete.cql]
      p2n carrot [--config=requete.cql]
      p2n interface [--config=requete.cql]
      p2n run [--config=requete.cql] [--with-family]
      p2n adhoc dump --expression=<expression> [--with-family] [--with-register]
      p2n adhoc list --expression=<expression> [--with-family]
      p2n adhoc worldmap --expression=<expression> --country-field=<country-field> [--with-family] [--with-register]
      p2n --version
      p2n (-h | --help)


    ------------
    Classic mode
    ------------
      p2n ops init                          Initialize Patent2Net with OPS OAuth credentials
      p2n acquire                           Run document acquisition
        --with-family                       Also run family data acquisition with "p2n acquire"
      p2n maps                              Build maps of country coverage of patents, as well as applicants and inventors
      p2n networks                          Build various artefacts for data exploration based on network graphs
      p2n tables                            Export various artefacts for tabular data exploration
      p2n bibfile                           Export data in bibfile format
      p2n iramuteq                          Fetch more data and export it to suitable format for using in Iramuteq
      p2n freeplane                         Build mind map for Freeplane
      p2n carrot                            Export data to XML suitable for using in Carrot
      p2n interface                         Build main Patent2Net html interface
      p2n run                               Run data acquisition and all formatters

    Options:
      --config=<config>                     Path to requete.cql. Will fall back to environment variable "P2N_CONFIG".

    Examples:

      # Initialize Patent2Net with OPS OAuth credentials
      p2n ops init --key=ScirfedyifJiashwOckNoupNecpainLo --secret=degTefyekDevgew1

      # Run query and gather data
      p2n acquire --config=/path/to/RequestsSets/Lentille.cql --with-family

      # Build all world maps
      p2n maps


    -----------
    Ad hoc mode
    -----------
      p2n ops init                          Initialize Patent2Net with OPS OAuth credentials
      p2n adhoc dump                        Display results for given query expression in Patent2Net format (JSON)
      p2n adhoc list                        Display list of publication numbers for given query expression
      p2n adhoc worldmap                    Generate world map for given query expression over given field

    Options:
      --expression=<expression>             Search expression in CQL format, e.g. "TA=lentille"
      --with-register                       Also acquire register information for each result hit.
                                            Required for "--country-field=designated_states".
      --country-field=<country-field>       Field name of country code for "p2n adhoc worldmap"
                                            e.g. "country", "applicants", "inventors", "designated_states"

    Examples:

      # Initialize Patent2Net with OPS OAuth credentials
      p2n ops init --key=ScirfedyifJiashwOckNoupNecpainLo --secret=degTefyekDevgew1

      # Run query and output results (JSON)
      p2n adhoc dump --expression='TA=lentille'

      # Run query and output list of publication numbers, including family members (JSON)
      p2n adhoc list --expression='TA=lentille' --with-family

      # Generate data for world maps using d3plus/geo_map (JSON)
      p2n adhoc worldmap --expression='TA=lentille' --country-field='country'
      p2n adhoc worldmap --expression='TA=lentille' --country-field='applicants'
      p2n adhoc worldmap --expression='TA=lentille' --country-field='inventors'
      p2n adhoc worldmap --expression='TA=lentille' --country-field='designated_states' --with-register
