# -*- coding: utf-8 -*-
# (c) 2017-2018 The Patent2Net Developers

import os
import epo_ops
import json
from P2N_Lib import LoadBiblioFile, RenderTemplate
from P2N_Config import LoadConfig
from PIL import Image
from p2n.util import to_png

THUMBNAIL_SIZE = 128, 128


def get_patent_label(patent):
    if isinstance(patent['label'], list):
        return patent['label'][0]
    return patent['label']


def generate_thumbnails(img_path):
    img_path = os.path.normpath(img_path)
    base_path, img_fname = os.path.split(img_path)
    p, ext = os.path.splitext(img_fname)
    thumb = p + '.tb.png'
    thumb_f = os.path.normpath(os.path.join(base_path, thumb))
    orig = p + '.png'
    orig_f = os.path.normpath(os.path.join(base_path, orig))
    if not os.path.exists(orig_f):
        print 'Converting image {}'.format(img_path)

        # PIL can not handle images with G4 compression
        """
        im = Image.open(img_path)
        im2 = im.convert('L')
        im2.thumbnail(THUMBNAIL_SIZE, Image.LANCZOS)
        im2.save(thumb_f, 'PNG')
        im = Image.open(img_path)
        im.save(orig_f, 'PNG')
        """

        # Use ImageMagick or other tooling
        with open(img_path) as tiff:

            tiff_payload = tiff.read()

            # Write original image in PNG format
            payload_orig = to_png(tiff_payload)
            with open(orig_f, 'w') as png_orig:
                png_orig.write(payload_orig)

            # Write thumbnail image in PNG format
            width, height = THUMBNAIL_SIZE
            payload_thumbnail = to_png(tiff_payload, width=width, height=height)
            with open(thumb_f, 'w') as png_thumbnail:
                png_thumbnail.write(payload_thumbnail)

    return thumb, orig, img_fname


configFile = LoadConfig()
requete = configFile.requete
IsEnableScript = configFile.GatherImages

ResultBiblioPath = configFile.ResultBiblioPath
ResultPathImages = configFile.ResultPathImages
P2NFamilly = configFile.GatherFamilly


if IsEnableScript:

    prefixes = ['']
    if P2NFamilly:
        prefixes.append('Families')

    for prefix in prefixes:
        ndf = prefix + configFile.ndf

        biblio_file = LoadBiblioFile(ResultBiblioPath, ndf)
        patents = biblio_file['brevets']
        gallery = []
        for patent in patents:
            patent_label = get_patent_label(patent)
            i = 1
            print 'Processing patent {}'.format(patent_label)
            path_img_base = '{}//{}-{}.tiff'.format(ResultPathImages, patent_label, '{}')
            path = path_img_base.format(i)
            while os.path.exists(path):
                thumb, orig, tiff = generate_thumbnails(path)
                gallery.append({
                    "_id": '{}-{}'.format(patent_label, i),
                    'thumb': thumb,
                    'orig': orig,
                    'label': patent['title'],
                    'ipcr7': patent['IPCR7'],
                    'code': patent_label,
                    'tiff': tiff,
                })
                i += 1
                path = path_img_base.format(i)
        # print gallery
        RenderTemplate(
            'ModeleImages.html',
            ResultPathImages + '/index' + prefix + '.html',
            request=requete.replace('"', ''),
            gallery=gallery,
            json=json.dumps(gallery),
        )
