##################
Patent2Net sandbox
##################



*****
Setup
*****
::

    git clone https://github.com/Patent2net/P2N.git
    cd P2N

    virtualenv --no-site-packages .venv27
    source .venv27/bin/activate

    python setup.py develop



*********
Configure
*********
Patent2Net needs your personal credentials for accessing the OPS API.
You have to provide them once as they are stored into the file
``cles-epo.txt`` in the current working directory.

There is a convenience command for initializing Patent2Net with your OPS credentials::

    p2n ops init --key=ScirfedyifJiashwOckNoupNecpainLo --secret=degTefyekDevgew1

.. note:: The Patent2Net scripts expect to find the file ``cles-epo.txt`` in the projects' root folder.



********
Synopsis
********


Acquire data from OPS
=====================
Run Patent2Net::

    p2n acquire --config=/path/to/RequestsSets/Lentille.cql

Alternatively, you can specify the path to the ``requete.cql`` using an environment variable::

    export P2N_CONFIG=`pwd`/RequestsSets/Lentille.cql

then, just run::

    # Acquire patent information from OPS
    p2n acquire

    # Acquire family data also
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


Ad hoc mode
===========
::

    p2n adhoc dump --expression='TA=lentille'

::

    p2n adhoc worldmap --expression='TA=lentille' --country-field='country'
    p2n adhoc worldmap --expression='TA=lentille' --country-field='Applicant-Country'
    p2n adhoc worldmap --expression='TA=lentille' --country-field='Inventor-Country'



Full output of "p2n --help"
===========================
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
      p2n run [--config=requete.cql] [--with-family]
      p2n adhoc dump --expression=<expression>
      p2n adhoc worldmap --expression=<expression> --country-field=<country-field>
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
      p2n adhoc worldmap                    Generate world map for given query expression over given field

    Options:
      --expression=<expression>             Search expression in CQL format, e.g. "TA=lentille"
      --country-field=<country-field>       Field name of country code for "p2n adhoc worldmap"
                                            e.g. "country", "Applicant-Country", "Inventor-Country"

    Examples:

      # Initialize Patent2Net with OPS OAuth credentials
      p2n ops init --key=ScirfedyifJiashwOckNoupNecpainLo --secret=degTefyekDevgew1

      # Run query and output results (JSON)
      p2n adhoc dump --expression='TA=lentille'

      # Generate data for world maps using d3plus/geo_map (JSON)
      p2n adhoc worldmap --expression='TA=lentille' --country-field='country'
      p2n adhoc worldmap --expression='TA=lentille' --country-field='Applicant-Country'
      p2n adhoc worldmap --expression='TA=lentille' --country-field='Inventor-Country'



****************
Misc information
****************

Install pygraphviz on Mac OS X::

    pip install --install-option="--include-path=/opt/local/include" --install-option="--library-path=/opt/local/lib" 'pygraphviz==1.3.1'

Optional::

    # Run minimal web server
    make webserver

    # Go to http://localhost:8001/DATA/

