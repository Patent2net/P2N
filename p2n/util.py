# -*- coding: utf-8 -*-
# (c) 2017-2018 The Patent2Net Developers
import os
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


@memoize
def find_convert():
    """
    Debian: aptitude install imagemagick
    /usr/bin/convert

    Mac OS X
    /opt/local/bin/convert

    Self-compiled
    /opt/imagemagick-7.0.2/bin/convert
    """

    candidates = [
        '/opt/imagemagick-7.0.2/bin/convert',
        '/opt/imagemagick/bin/convert',
        '/opt/local/bin/convert',
        '/usr/bin/convert',
        ]
    return find_program_candidate(candidates)

def find_program_candidate(candidates):
    for candidate in candidates:
        if os.path.isfile(candidate):
            return candidate

def to_png(tiff_payload, format='tif', width='', height=''):

    width = str(width)
    height = str(height)

    # Unfortunately, PIL can not handle G4 compression.
    # Failure: exceptions.IOError: decoder group4 not available
    # Maybe patch: http://mail.python.org/pipermail/image-sig/2003-July/002354.html
    """
    import Image
    png = StringIO.StringIO()
    try:
        Image.open(StringIO.StringIO(tiff_payload)).save(png, 'PNG')
        png.seek(0)
    except Exception, e:
        print "ERROR (PIL+G4)!", e
        pass
    """

    """
    Instructions for installing ImageMagick on Debian::

        apt install imagemagick

    Instructions for installing ImageMagick on Windows::

        https://www.imagemagick.org/script/download.php#windows

    Instructions for building ImageMagick on Debian::

        # https://packages.debian.org/source/wheezy/imagemagick
        aptitude install build-essential checkinstall ghostscript libbz2-dev libexif-dev fftw-dev libfreetype6-dev libjasper-dev libjpeg-dev liblcms2-dev liblqr-1-0-dev libltdl-dev libpng-dev librsvg2-dev libtiff-dev libx11-dev libxext-dev libxml2-dev zlib1g-dev liblzma-dev libpango1.0-dev

        ./configure --prefix=/opt/imagemagick-7.0.2
        wget http://www.imagemagick.org/download/ImageMagick.tar.gz
        # untar and cd
        make -j6 && make install

    """


    # Let's resort to use ImageMagick! ;-(
    # http://www.imagemagick.org/pipermail/magick-users/2003-May/008869.html
    #convert_bin = os.path.join(os.path.dirname(__file__), 'imagemagick', 'convert.exe')

    more_args = []

    # Compute size for "resize" parameter
    size = ''
    if width or height:
        if width:
            size += width
        size += 'x'
        if height:
            size += height

        more_args += ['-resize', size]

    convert = find_convert()
    #command = [convert, 'tif:-', '+set', 'date:create', '+set', 'date:modify', 'png:-']
    command = [
        convert,
        #'{0}:-'.format(format),
        '-',                            # Convert from any format
        '+set', 'date:create', '+set', 'date:modify',
        # FIXME: make this configurable
        #'-resize', '530x',
        '-colorspace', 'rgb', '-flatten', '-depth', '8',
        '-antialias', '-quality', '100', '-density', '300',
        #'-level', '30%,100%',
        ] \
        + more_args + \
        ['png:-']

    command_debug = ' '.join(command)

    proc = subprocess.Popen(
        command,
        shell = (os.name == 'nt'),
        #shell = True,
        stdin = subprocess.PIPE,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
    )

    stdout = stderr = ''

    logger.info('Running command {}'.format(command_debug))
    try:
        stdout, stderr = proc.communicate(tiff_payload)
        if proc.returncode is not None and proc.returncode != 0:
            raise Exception('TIFF to PNG conversion failed')
    except:
        logger.error('TIFF to PNG conversion failed, {1}. returncode={2}, command="{0}"'.format(command_debug, stderr, proc.returncode))
        raise Exception('TIFF to PNG conversion failed')

    if 'ImageMagick' in stdout[:200]:
        logger.error('TIFF to PNG conversion failed, stdout={1}, stderr={1}. command="{0}"'.format(command_debug, stdout, stderr))
        raise Exception('TIFF to PNG conversion failed')

    return stdout
