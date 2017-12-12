# -*- coding: utf-8 -*-
# (c) 2017 The Patent2Net Developers
import sys
import time
import types
import logging
import operator
import functools
import itertools
import traceback
import subprocess
from StringIO import StringIO
from json.encoder import JSONEncoder
from collections import OrderedDict

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

def filterdict(dct, keys=None):
    """Filter dictionaries using specified keys"""
    keys = keys or []
    dct = {key: value for (key, value) in dct.iteritems() if key in keys}
    return dct

def dictproduct(dct):
    """
    Compute combinations from dictionary with list values
    by calculating the cartesian product.
    """
    # https://stackoverflow.com/questions/3873654/combinations-from-dictionary-with-list-values-using-python/41870264#41870264

    # Bring dictionary into a form suitable for computing the cartesian product
    for key, value in dct.iteritems():

        # Use empty string for empty values
        if value is None or value == [] or value == [None]:
            value = ''

        # Let's make everything a list
        value = to_list(value)

        dct[key] = value

    # Yield dictionaries making up all combinations of multiple values
    # reduced to dictionaries containing single scalar values only.
    for t in itertools.product(*dct.itervalues()):
        yield dict(zip(dct.iterkeys(), t))


class JsonObjectEncoder(JSONEncoder):
    """
    Serialize nested object compositions to JSON
    """
    def default(self, o):
        # TODO: Maybe use "o.asdict()"?
        return o.__dict__


def unique(data):
    return list(set(data))


def object_to_dictionary(obj, rules):
    """
    Transform object to dictionary according to set of rules.
    For an example, see ``p2n.formatter.tables.pivottables_data_documents``.

    TODO: Provide examples of rule format, input and output data.
    """

    data = OrderedDict()

    for rule in rules:
        key = value = None

        if isinstance(rule, types.StringType):
            key = rule
            try:
                value = operator.attrgetter(rule)(obj)
            except AttributeError:
                pass

        elif isinstance(rule, types.DictionaryType):
            key = rule['name']
            value = rule['getter'](obj)

            if 'recipe' in rule:
                recipe = rule['recipe']
                value = recipe(value)

        if key:
            data[key] = value

    return data


def exception_traceback(exc_info=None):
    """
    Return a string containing a traceback message for the given
    exc_info tuple (as returned by sys.exc_info()).

    from setuptools.tests.doctest
    """

    if not exc_info:
        exc_info = sys.exc_info()

    # Get a traceback message.
    excout = StringIO()
    exc_type, exc_val, exc_tb = exc_info
    traceback.print_exception(exc_type, exc_val, exc_tb, file=excout)
    return excout.getvalue()
