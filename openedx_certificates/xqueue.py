# -*- coding: utf-8 -*-
"""
XQueue management wrapper
"""
import json

import logging
import logging.config
import requests
from requests.exceptions import ConnectionError
from requests.exceptions import Timeout

# import settings # TODO
from openedx_certificates import settings
from openedx_certificates import strings
from openedx_certificates.exceptions import EmptyQueue
from openedx_certificates.exceptions import FailedRequest
from openedx_certificates.exceptions import InvalidReturnCode
from openedx_certificates.exceptions import prettify

# logging.config.dictConfig(settings.LOGGING)
logging.config.dictConfig(settings.get('LOGGING'))
LOG = logging.getLogger(__name__)


class XQueue(object):
    """
    Provide an interface to the XQueue server
    """

    def __init__(self):
        """
        Initialize a new XQueue
        """
        LOG.debug("Initialize {type}: ".format(type=type(self)))
        self.url = settings.get('QUEUE_URL')
        self.name = settings.get('QUEUE_NAME')
        self.auth_basic = (
            settings.get('QUEUE_AUTH_USER'),
            settings.get('QUEUE_AUTH_PASS'),
        )
        self.auth_xqueue = (
            settings.get('QUEUE_USER'),
            settings.get('QUEUE_PASS'),
        )
        self.session = None
        LOG.debug("Initialized {type}: {self}".format(type=type(self), self=self))

    def __str__(self):
        """
        Stringify self as the URL
        """
        return self.url

    def __iter__(self):
        """
        Allow the queue to be iterated over
        """
        return self

    def next(self):
        """
        Get submission from the XQueue server
        :returns: dict -- a single submission
        """
        LOG.debug("Get next submission")
        try:
            self._try_login()
            response = self._request(
                self.session.get,
                'get_submission',
                params={
                    'queue_name': self.name,
                },
            )
            LOG.info(
                strings.MESSAGE_RESPONSE,
                {
                    'response': response,
                },
            )
            content = json.loads(response['content'])
            response = _parse_xqueue_response(content)
            LOG.debug("Got next submission: {response}".format(response=response))
            return response
        except FailedRequest:
            pass
        except EmptyQueue:
            pass
        except Exception as error:
            error = prettify(error)
            LOG.critical('UNCAUGHT ERROR: %s', error)
        raise StopIteration

    def post(self, header, **kwargs):
        """
        Reply to LMS with creation result
        :param header: A dictionary of request headers
        :type header: dict
        :param kwargs: The request body
        :type header: dict
        """
        data = {
            'xqueue_header': json.dumps(header),
            'xqueue_body': json.dumps(kwargs),
        }
        LOG.info(
            strings.MESSAGE_POST,
            {
                'data': data,
            },
        )
        self._try_login()
        try:
            response = self._request(self.session.post, 'put_result', data=data)
        except FailedRequest as error:
            return None
        LOG.info(
            strings.MESSAGE_RESPONSE,
            {
                'response': response,
            },
        )
        return response

    def _try_login(self):
        """
        Login to the XQueue server, if not already
        :param auth_basic: A tuple of (username, password)
        :type auth_basic: tuple
        :param auth_xqueue: A tuple of (username, password)
        :type auth_xqueue: tuple
        """
        if not self.session:
            self.session = requests.Session()
            self.session.auth = self.auth_basic
            data = {
                'username': self.auth_xqueue[0],
                'password': self.auth_xqueue[1],
            }
            try:
                response = self._request(self.session.post, 'login', data=data)
            except FailedRequest:
                response = None
            if not response:
                return False
        return True

    def _request(self, method, url, **kwargs):
        """
        Make a request to the XQueue server
        :param method: The method to be executed by the server
        :type method: str
        :param url: The server URL
        :type url: str
        :returns: dict -- A dictionary of the JSON response
        """
        url = "{url_base}/xqueue/{method}/".format(
            url_base=self.url,
            method=url,
        )
        try:
            request = method(url, **kwargs)
        except (ConnectionError, Timeout) as error:
            LOG.error(error)
            raise FailedRequest('Failed Request')
        try:
            response = request.json()
        except ValueError as error:
            LOG.error(error)
            raise FailedRequest('Failed Request')
        try:
            _validate(response)
        except InvalidReturnCode as error:
            LOG.error(error)
            raise FailedRequest('Failed Request')
        return response



def _validate(response):
    """
    Check for a valid return code in XQueue response
    :param response: The server response
    :type response: dict
    :raises: InvalidReturnCode
    :returns: bool - Whether or not the response is valid
    """
    return_code = response.get('return_code')
    if return_code != 0:
        content = response.get('content', '')
        if return_code == 1 and content.startswith('Queue ') and content.endswith(' is empty'):
            raise EmptyQueue(response)
        raise InvalidReturnCode(
            strings.ERROR_VALIDATE.format(
                return_code=return_code,
                response=response,
            )
        )
    return True


def _parse_xqueue_response(response):
    LOG.debug("Parse response: %s", response)
    header = json.loads(response['xqueue_header'])
    body = json.loads(response['xqueue_body'])
    LOG.debug("Parsed response header: %s", header)
    LOG.debug("Parsed response body: %s", body)
    return (header, body)
