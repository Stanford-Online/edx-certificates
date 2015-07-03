# -*- coding: utf-8 -*-

"""
Settings file for the certificate agent
"""

import json
import os
import yaml

from logsettings import get_logger_config
from path import path

import openedx_certificates

ROOT_PATH = path(__file__).dirname()
REPO_PATH = ROOT_PATH
ENV_ROOT = REPO_PATH.dirname()

# Override CERT_PRIVATE_DIR if you have have private templates, fonts, etc.
CERT_PRIVATE_DIR = REPO_PATH

# If CERT_PRIVATE_DIR is set in the environment use it

if 'CERT_PRIVATE_DIR' in os.environ:
    CERT_PRIVATE_DIR = path(os.environ['CERT_PRIVATE_DIR'])

# This directory and file must exist in CERT_PRIVATE_DIR
# if you are using custom templates and custom cert config
TEMPLATE_DATA_SUBDIR = 'template_data'
CERT_DATA_FILE = 'cert-data.yml'

# DEFAULTS
DEBUG = False
# This needs to be set on MacOS or anywhere you want logging to simply go
# to an output file.
LOGGING_DEV_ENV = True
LOGGING = get_logger_config(ENV_ROOT,
                            logging_env="dev",
                            local_loglevel="INFO",
                            dev_env=LOGGING_DEV_ENV,
                            debug=False)

# Default for the gpg dir
# Specify the CERT_KEY_ID before running the test suite
CERT_GPG_DIR = '{0}/.gnupg'.format(os.environ['HOME'])
# dummy key:
# https://raw.githubusercontent.com/edx/configuration/master/playbooks/roles/certs/files/example-private-key.txt
CERT_KEY_ID = 'FEF8D954'
# or leave blank to skip gpg signing
# CERT_KEY_ID = ''

# Update this with your bucket name
CERT_WEB_ROOT = '/var/tmp'
# when set to true this will copy the generated certificate
# to the CERT_WEB_ROOT. This is not something you want to do
# unless you are running your certificate service on a single
# server
COPY_TO_WEB_ROOT = False
S3_UPLOAD = True
S3_VERIFY_PATH = 'cert'

# Programmatic disclaimer text
CERTS_SITE_DISCLAIMER_TEXT = (
    '<b>PLEASE NOTE:</b> SOME ONLINE COURSES MAY DRAW ON MATERIAL FROM COURSES TAUGHT ON-CAMPUS BUT THEY ARE NOT '
    'EQUIVALENT TO ON-CAMPUS COURSES. THIS STATEMENT DOES NOT AFFIRM THAT THIS PARTICIPANT WAS ENROLLED AS A STUDENT '
    'AT STANFORD UNIVERSITY IN ANY WAY. IT DOES NOT CONFER A STANFORD UNIVERSITY GRADE, COURSE CREDIT OR DEGREE, AND '
    'IT DOES NOT VERIFY THE IDENTITY OF THE PARTICIPANT.'
)

# These are initialized below, after the environment is read
CERT_URL = ''
CERT_DOWNLOAD_URL = ''
CERT_VERIFY_URL = ''

LOG_DIR = openedx_certificates.settings.get('LOG_DIR')

# load settings from env.json and auth.json
if os.path.isfile(ENV_ROOT / "env.json"):
    with open(ENV_ROOT / "env.json") as env_file:
        ENV_TOKENS = json.load(env_file)
    CERT_GPG_DIR = ENV_TOKENS.get('CERT_GPG_DIR', CERT_GPG_DIR)
    CERT_KEY_ID = ENV_TOKENS.get('CERT_KEY_ID', CERT_KEY_ID)
    CERT_URL = ENV_TOKENS.get('CERT_URL', '')
    CERT_DOWNLOAD_URL = ENV_TOKENS.get('CERT_DOWNLOAD_URL', "")
    CERT_VERIFY_URL = ENV_TOKENS.get('CERT_VERIFY_URL', "")
    CERT_WEB_ROOT = ENV_TOKENS.get('CERT_WEB_ROOT', CERT_WEB_ROOT)
    COPY_TO_WEB_ROOT = ENV_TOKENS.get('COPY_TO_WEB_ROOT', COPY_TO_WEB_ROOT)
    S3_UPLOAD = ENV_TOKENS.get('S3_UPLOAD', S3_UPLOAD)
    S3_VERIFY_PATH = ENV_TOKENS.get('S3_VERIFY_PATH', S3_VERIFY_PATH)
    CERTS_SITE_DISCLAIMER_TEXT = ENV_TOKENS.get('CERT_SITE_DISCLAIMER_TEXT', CERTS_SITE_DISCLAIMER_TEXT)
    local_loglevel = ENV_TOKENS.get('LOCAL_LOGLEVEL', 'INFO')
    LOGGING_DEV_ENV = ENV_TOKENS.get('LOGGING_DEV_ENV', True)
    LOGGING = get_logger_config(LOG_DIR,
                                logging_env=ENV_TOKENS.get('LOGGING_ENV', 'dev'),
                                local_loglevel=local_loglevel,
                                debug=False,
                                dev_env=LOGGING_DEV_ENV,
                                service_variant=os.environ.get('SERVICE_VARIANT', None))
    CERT_PRIVATE_DIR = ENV_TOKENS.get('CERT_PRIVATE_DIR', CERT_PRIVATE_DIR)

CERT_BUCKET = openedx_certificates.settings.get('CERT_BUCKET')
# This is the base URL used for logging CERT uploads to s3
CERT_URL = CERT_URL or 'http://{}.s3.amazonaws.com'.format(CERT_BUCKET)
# This is the base URL that will be displayed to the user in the dashboard
# It's different than CERT_URL because because CERT_URL will not have a valid
# SSL certificate. # FIXME: confirm whether this is true
CERT_DOWNLOAD_URL = CERT_DOWNLOAD_URL or 'https://{}.s3.amazonaws.com'.format(CERT_BUCKET)
CERT_VERIFY_URL = CERT_VERIFY_URL or 'http://{}.s3.amazonaws.com'.format(CERT_BUCKET)

# Use the custom CERT_PRIVATE_DIR for paths to the
# template sub directory and the cert data config

TEMPLATE_DIR = os.path.join(CERT_PRIVATE_DIR, TEMPLATE_DATA_SUBDIR)

with open(os.path.join(CERT_PRIVATE_DIR, CERT_DATA_FILE)) as f:
    CERT_DATA = yaml.load(f.read().decode("utf-8"))

# Locale and Translations
DEFAULT_LOCALE = 'en_US'
DEFAULT_TRANSLATIONS = {
    'en_US': {
        'success_text': u'has successfully completed a free online offering of',
        'grade_interstitial': u"with {grade}.",
        'disclaimer_text': CERTS_SITE_DISCLAIMER_TEXT,
        'verify_text': u"Authenticity can be verified at {verify_link}",
    },
}
