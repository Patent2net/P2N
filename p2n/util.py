# -*- coding: utf-8 -*-
# (c) 2017 The Patent2Net Developers
import sys
import time
import logging
import functools
import subprocess

logger = logging.getLogger(__name__)

def setup_logging(level=logging.INFO):
    log_format = '%(asctime)-15s [%(name)-25s] %(levelname)-7s: %(message)s'
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
    process = subprocess.Popen(command, shell=True, bufsize=1, cwd=directory)

    # Poll process for new output until finished
    while True:

        try:
            outcome = process.poll()

            if outcome is not None:
                returncode = process.returncode
                if returncode != 0:
                    logger.error('Command "{command}" failed with return code {returncode}'.format(**locals()))
                return returncode

            time.sleep(1)

        except KeyboardInterrupt:
            logger.warning('Terminating script {}'.format(script))
            process.terminate()
            process.wait()
            return process.returncode

def memoize(obj):
    """
    https://wiki.python.org/moin/PythonDecoratorLibrary#Memoize
    """
    cache = obj.cache = {}

    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = obj(*args, **kwargs)
        return cache[key]

    return memoizer

def to_list(obj):
    """Convert an object to a list if it is not already one"""
    if not isinstance(obj, (list, tuple)):
        obj = [obj, ]
    return obj
