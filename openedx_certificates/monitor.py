# -*- coding: utf-8 -*-
import os
import sys
import time

import logging

from openedx_certificates import settings
from gen_cert import CertificateGen
from openedx_certificates import strings
from openedx_certificates.xqueue import XQueue
from openedx_certificates.exceptions import prettify


logging.config.dictConfig(settings.get('LOGGING'))
LOG = logging.getLogger(__name__)


class Monitor(object):
    def __init__(self, **kwargs):
        """
        :param seconds_to_sleep: Seconds to sleep between failed requests
        :type seconds_to_sleep: int
        """
        LOG.debug('Initialize %s', type(self))
        self.seconds_to_sleep = kwargs.get('sleep_seconds')
        self.xqueue = XQueue()
        LOG.debug('Initialized %s: %s', type(self), self)

    def process(self, iterations=float('inf')):
        """
        Process the XQueue
        """
        course_id = None
        certificate_generator = None
        LOG.debug('Process %s iterations', iterations)
        while iterations > 0:
            iterations -= 1
            for response in self.xqueue:
                LOG.debug('Next XQueue response: %s', response)
                header, body = response
                if 'course_id' not in body:
                    continue
                if course_id != body['course_id']:
                    course_id = body['course_id']
                    certificate_generator = self._get_certificate_generator(header, body)
                    if not certificate_generator:
                        continue
                dummy0, username, grade, download_url = self._create_and_upload(certificate_generator, header, body)
                LOG.info('Created cert: %s,%s,%s,%s', course_id, username, grade, download_url)
                if iterations < 1:
                    break
            LOG.debug('Queue is empty; sleep %d seconds; %f more to go', self.seconds_to_sleep, iterations)
            time.sleep(self.seconds_to_sleep)
        LOG.debug('Processed iterations')

    def _create_and_upload(self, certificate_generator, header, body):
        download_url = None
        LOG.debug(
            strings.MESSAGE_GENERATE,
            {
                'username': body['username'].encode('utf-8'),
                'name': body['name'].encode('utf-8'),
                'course_id': body['course_id'].encode('utf-8'),
                'grade': body['grade'],
            },
        )
        try:
            (download_uuid, verify_uuid, download_url) = certificate_generator.create_and_upload(
                body['name'].encode('utf-8'),
                grade=body['grade'],
                designation=body['designation'],
            )
        except Exception as error:
            error_reason = prettify(error, header, body)
            LOG.error(
                strings.ERROR_GENERATE,
                {
                    'error': error_reason,
                },
            )
            self.xqueue.post(
                header,
                error=strings.ERROR_PARSE.format(
                    error=error,
                    header_body=error_reason,
                ),
                username=body['username'],
                course_id=body['course_id'],
                error_reason=error_reason,
            )
            return None
        self.xqueue.post(
            header,
            action=body['action'],
            download_uuid=download_uuid,
            verify_uuid=verify_uuid,
            username=body['username'],
            course_id=body['course_id'],
            url=download_url,
        )
        return (
            body['course_id'],
            body['username'],
            body['grade'],
            download_url,
        )

    def _get_certificate_generator(self, header, body):
        try:
            certificate_generator = CertificateGen(
                body['course_id'],
                body['template_pdf'],
                aws_id=settings.get('CERT_AWS_ID'), # TODO: remove
                aws_key=settings.get('CERT_AWS_KEY'), # TODO: remove
                long_course=body['course_name'],
                issued_date=body['issued_date'],
            )
        except (TypeError, ValueError, KeyError, IOError) as error:
            LOG.critical(
                strings.ERROR_PARSE,
                {
                    'error': error,
                    'header_body': (header, body),
                },
            )
            certificate_generator = None
        return certificate_generator
