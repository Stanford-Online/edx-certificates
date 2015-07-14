# -*- coding: utf-8 -*-
"""
Define custom error and message strings
"""

ERROR_EXCEPTION = (
    "username={username}, course_id={course_id}: "
    "{exception_type} {file_name}:{line_number} {exception}"
)
ERROR_GENERATE = "An error occurred during certificate generation: {error}"
ERROR_LEN = "Unable to get queue length: {error}"
ERROR_PARSE = "Unable to parse queue submission ({error}): {header_body}"
# ERROR_PROCESS = "There was an error processing the certificate request: {error}"
ERROR_VALIDATE = "Invalid return code ({return_code}): {response}"
# MESSAGE_GET = "XQueue response: %s"
MESSAGE_GENERATE = (
    "Generating certificate for user {username} ({name}), "
    "in {course_id}, with grade {grade}"
)
# MESSAGE_ITERATIONS = "%s iterations remaining"
MESSAGE_LENGTH = "queue length: {length}: {xqueue}"
MESSAGE_POST = "Posting result to the LMS: {data}"
MESSAGE_RESPONSE = "Response: {response}"
