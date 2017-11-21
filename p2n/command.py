# -*- coding: utf-8 -*-
# (c) 2017 The Patent2Net Developers
import os
import sys
import logging
from docopt import docopt
from p2n import __version__
from p2n.config import OPSCredentials
from p2n.util import boot_logging, normalize_docopt_options, run_script

logger = logging.getLogger(__name__)

APP_NAME = 'Patent2Net'

def run():
    """
    Usage:
      p2n ops init --key=<ops-oauth-key> --secret=<ops-oauth-secret>
      p2n acquire [--with-family] [--config=requete.cql]
      p2n maps [--config=requete.cql]
      p2n networks [--config=requete.cql]
      p2n tables [--config=requete.cql]
      p2n bibfile [--config=requete.cql]
      p2n iramuteq [--config=requete.cql]
      p2n freeplane [--config=requete.cql]
      p2n carrot [--config=requete.cql]
      p2n --version
      p2n (-h | --help)

    About:
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

    Common options:
      --config=<config>                     Path to requete.cql. Will fall back to environment variable "P2N_CONFIG".

    """

    # Use generic commandline options schema and amend with current program name
    commandline_schema = (run.__doc__).format(program=APP_NAME)

    # Read commandline options
    options = docopt(commandline_schema, version=APP_NAME + ' ' + __version__)

    # Start logging subsystem
    boot_logging(options)

    # Clean option names
    options = normalize_docopt_options(options)

    # Debugging
    #print('Options:\n{}'.format(pformat(options)))

    # Boot Pyramid to access the database
    configfile = options['config']
    if not configfile:
        configfile = os.environ.get('P2N_CONFIG')

    if not configfile:
        logger.error('No configuration file given. Either use --config commandline argument or P2N_CONFIG environment variable')
        sys.exit(1)

    if options['ops'] and options['init']:
        if options['key'] and options['secret']:
            c = OPSCredentials()
            c.write(options['key'], options['secret'])

    if options['acquire']:
        run_script('OPSGatherPatentsv2.py', configfile)
        if options['with-family']:
            run_script('OPSGatherAugment-Families.py', configfile)

    if options['maps']:
        run_script('FormateExportAttractivityCartography.py', configfile)
        run_script('FormateExportCountryCartography.py', configfile)

    if options['bibfile']:
        run_script('FormateExportBiblio.py', configfile)

    if options['tables']:
        run_script('FormateExportDataTableFamilies.py', configfile)
        run_script('FormateExportDataTable.py', configfile)
        run_script('FormateExportPivotTable.py', configfile)

    if options['networks']:

        networks = [
            "CountryCrossTech",
            "CrossTech",
            "InventorsCrossTech",
            "Applicants_CrossTech",
            "Inventors",
            "ApplicantInventor",
            "Applicants",
            "References",
            "Citations",
            "Equivalents",
        ]

        for network in networks:
            run_script('P2N-PreNetworks.py {network}'.format(network=network), configfile)
            run_script('P2N-Networks.py {network}'.format(network=network), configfile)
            run_script('P2N-NetworksJS.py {network}'.format(network=network), configfile)

    if options['iramuteq']:
        run_script('OPSGatherContentsV2-Iramuteq.py', configfile)
        run_script('FusionIramuteq2.py', configfile)

    if options['freeplane']:
        run_script('P2N-FreePlane.py', configfile)

    if options['carrot']:
        run_script('FusionCarrot2.py', configfile)
