# -*- coding: utf-8 -*-
"""
Raise custom exceptions
"""
import os.path
import sys

from openedx_certificates import strings

class InvalidReturnCode(Exception):
    """
    Raise when XQueue reponse contains an invalid return_code
    """
    pass


class EmptyQueue(Exception):
    pass


class FailedRequest(Exception):
    pass


def prettify(error, header=None, body=None):
    header = header or {}
    body = body or {}
    exc_type, dummy0, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    error_reason = strings.ERROR_EXCEPTION.format(
        username=body.get('username'),
        course_id=body.get('course_id'),
        exception_type=exc_type,
        exception=error,
        file_name=fname,
        line_number=exc_tb.tb_lineno,
    )
    return error_reason
