#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This is a standalone utility for generating certficiates.
It will use test data in tests/test_data.py for names and courses.
PDFs by default will be dropped in TMP_GEN_DIR for review

TODO: modes
- read from CSV: create many certs
- read from command line: create single cert
- write output to CSV and/or stdout
- optionally upload to S3

CHANGELOG:
- report output format is changed:
    - was: name, course, args.long_org, args.long_course, download_url,
    - now: course_id, name, grade, download_url
- logging format change: s/{hostname} /pid:/
- Doesn't upload to S3 by default
"""
from argparse import ArgumentParser, RawTextHelpFormatter
import csv
import logging
import os
import random
import shutil
import sys

from gen_cert import CertificateGen
from openedx_certificates import settings


logging.config.dictConfig(settings.get('LOGGING'))
LOG = logging.getLogger('certificates.create_pdfs')


def parse_args():
    parser = ArgumentParser(
        description=__doc__,
        formatter_class=RawTextHelpFormatter,
    )
    parser.add_argument(
        '-c',
        '--course',
        help='optional course_id',
    )
    parser.add_argument(
        '-n',
        '--name',
        help='optional names for the cert',
        action='append',
        dest='names',
    )
    parser.add_argument(
        '-g',
        '--grade',
        help='optional grading label to apply',
    )

    parser.add_argument(
        '-T',
        '--title-random',
        help='add random title after name',
        default=False,
        action='store_true',
    )
    args = parser.parse_args()
    args = vars(args)
    return args


def main(args):
    """
    Generates some pdfs using each template for different names for
    review in a pdf viewer.
    Will copy out the pdfs into the certs/ dir
    """
    LOG.debug('Launching %s', __name__)
    copy_dir = settings.get('TMP_GEN_DIR') + "+copy"
    certificate_data = []
    course = args.get('course')
    courses = settings.get('CERT_DATA').keys()
    grade = args.get('grade')
    names = args.get('names', [])

    if course:
        courses = [course]

    try:
        os.makedirs(copy_dir)
        LOG.debug('Makedirs: %s', copy_dir)
    except OSError:
        pass

    for course in courses:
        for name in names:
            cert = CertificateGen(
                course,
                # TODO: we shouldn't pass AWS creds along
                aws_id=settings.get('CERT_AWS_ID'),
                aws_key=settings.get('CERT_AWS_KEY'),
            )
            title = None
            if args.get('title_random'):
                title = random.choice(stanford_cme_titles)[0]
            (download_uuid, verify_uuid, download_url) = cert.create_and_upload(
                name,
                upload=settings.get('S3_UPLOAD'),
                copy_to_webroot=False,
                cleanup=False,
                designation=title,
                grade=grade,
            )
            certificate_data.append(
                (
                    course,
                    name,
                    grade,
                    download_url,
                )
            )
            directory_output = os.path.join(
                cert.dir_prefix,
                settings.get('S3_CERT_PATH'),
                download_uuid,
            )
            copy_dest = "{copy_dir}/{course}-{name}.pdf".format(
                copy_dir=copy_dir,
                name=name.replace(' ', '-').replace('/', '-'),
                course=course.replace('/', '-')
            )

            if _try_copy_file(
                directory_output,
                copy_dest,
                name,
                download_uuid,
                verify_uuid,
            ):
                LOG.info("Created %s", copy_dest)
            else:
                LOG.error("Unable to copy file: %s", copy_dest)
    csv_writer = csv.writer(sys.stdout, quoting=csv.QUOTE_ALL)
    csv_writer.writerows(rows)
    LOG.debug('Closing %s', __name__)


def _try_copy_file(
    directory_output,
    copy_dest,
    name,
    download_uuid,
    verify_uuid,
):
    try:
        shutil.copyfile(
            "{0}/{1}".format(
                directory_output,
                settings.get('CERT_FILENAME'),
            ),
            unicode(copy_dest.decode('utf-8'))
        )
    except Exception as error:
        LOG.error(
            "{error}: {name}: {download_uuid}: {verify_uuid}: {download_uuid}: {directory_output}: {copy_dest}",
            {
                'error': error,
                'name': name,
                'download_uuid': download_uuid,
                'verify_uuid': verify_uuid,
                'download_uuid': download_uuid,
                'directory_output': directory_output,
                'copy_dest': copy_dest,
            },
        )
        raise
    return True


if __name__ == '__main__':
    LOG = logging.getLogger('openedx_certificates.bin.create')
    args = parse_args()
    main(args)
