#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generate OpenEdX certificates
-----------------------------

This script will continuously monitor a queue for certificate
generation, it does the following:

    * Connect to the xqueue server
    * Pull a single certificate request
    * Process the request
    * Post a result back to the xqueue server

CHANGELOG: Don't pass AWS secrets via command line
    - You can see these with `ps`!
"""
from argparse import ArgumentParser, RawTextHelpFormatter
import logging

from openedx_certificates import settings
from openedx_certificates.monitor import Monitor


logging.config.dictConfig(settings.get('LOGGING'))
LOG = logging.getLogger(__name__)


def parse_args():
    parser = ArgumentParser(
        description=__doc__,
        formatter_class=RawTextHelpFormatter,
    )
    parser.add_argument(
        '--sleep-seconds',
        default=5,
        help='Number of seconds to sleep when XQueue is empty',
    )
    args = parser.parse_args()
    args = vars(args)
    return args


def main(args=None):
    LOG.debug('Launching %s', __name__)
    args = args or {}
    monitor = Monitor(**args)
    monitor.process(iterations=5)
    LOG.debug('Closing %s', __name__)


if __name__ == '__main__':
    LOG = logging.getLogger('openedx_certificates.bin.watch')
    args = parse_args()
    main(args)
