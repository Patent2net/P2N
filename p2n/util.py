# -*- coding: utf-8 -*-
# (c) 2017 The Patent2Net Developers
import sys
import time
import logging
import subprocess

logger = logging.getLogger(__name__)

def setup_logging(level=logging.INFO):
    log_format = '%(asctime)-15s [%(name)-20s] %(levelname)-7s: %(message)s'
    logging.basicConfig(
        format=log_format,
        stream=sys.stderr,
        level=level)

def boot_logging(options=None):
    log_level = logging.INFO
    if options and options.get('--debug'):
        log_level = logging.DEBUG
    setup_logging(level=log_level)

def normalize_docopt_options(options):
    normalized = {}
    for key, value in options.items():
        key = key.strip('--<>')
        normalized[key] = value
    return normalized

def run_script(script, configfile, directory='Patent2Net'):

    # Compute command
    command = 'python {script} {configfile}'.format(script=script, configfile=configfile)
    logger.info('Running command "{}"'.format(command))

    # Run process
    process = subprocess.Popen(command, shell=True, bufsize=1, stderr=subprocess.PIPE, cwd=directory)

    # Poll process for new output until finished
    while True:

        try:
            outcome = process.poll()

            if outcome is not None:
                returncode = process.returncode
                if returncode != 0:
                    stderr = process.stderr.read()
                    logger.error('Command "{command}" failed with return code {returncode}\n{stderr}'.format(**locals()))
                return returncode

            time.sleep(1)

        except KeyboardInterrupt:
            logger.warning('Terminating script {}'.format(script))
            process.terminate()
            process.wait()
            return returncode
