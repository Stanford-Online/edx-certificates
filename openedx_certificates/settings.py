# -*- coding: utf-8 -*-
"""
Load settings from JSON
"""

import json
import os

import yaml

from logsettings import get_logger_config


def _load_json(filepath, filename):
    path_json = os.path.join(filepath, filename)
    try:
        with open(path_json) as file_json:
            result = json.load(file_json)
    except IOError:
        result = {}
    return result


def _load_environ(prefix='CERT_'):
    environ = {}
    for key in os.environ:
        if key.startswith(prefix):
            environ[key] = os.environ[key]
    return environ


_path_file = os.path.abspath(__file__)
_path_module = os.path.dirname(_path_file)
_path_package = os.path.dirname(_path_module)
_path_application = os.path.dirname(_path_package)

_all = {}
_memory = {}
_log = {}


def _reload():
    global _all, _memory, _log
    _auth = _load_json(_path_application, 'auth.json')
    _env = _load_json(_path_application, 'env.json')
    _default = _load_json(_path_module, 'config.json')
    _environ = _load_environ()
    _memory = {}
    _custom = {}
    _custom.update(_env)
    _custom.update(_auth)
    _all = {}
    _all.update(_default)
    _all.update(_custom)
    _all.update(_environ)
    _log_default = _load_json(_path_module, 'log.json')
    _log_custom = _load_json(_path_application, 'log.json')
    _log = {}
    _log.update(_log_default)
    # _log.update(_log_custom)


def get(key, default=None, course_id=None):
    def _get(key, default=None):
        return _all.get(key, default)
    if course_id:
        if course_id in _get('CERT_DATA'):
            if key in _get('CERT_DATA')[course_id]:
                return _get('CERT_DATA')[course_id][key]
    return _get(key, default)


def update(key, value):
    _memory[key] = value
    _all[key] = value
    return value


_reload()

if not get('CERT_GPG_DIR'):
    _cert_gpg_dir = "{0}/.gnupg".format(
        os.environ['HOME'],
    )
    update('CERT_GPG_DIR', _cert_gpg_dir)

if get('CERT_PRIVATE_DIR') and get('TEMPLATE_DATA_SUBDIR'):
    _template_dir = os.path.join(
        get('CERT_PRIVATE_DIR'),
        get('TEMPLATE_DATA_SUBDIR'),
    )
    update(u'TEMPLATE_DIR', _template_dir)

if get('CERT_DATA_FILE') and get('CERT_PRIVATE_DIR'):
    _cert_data_file = os.path.join(
        get('CERT_PRIVATE_DIR'),
        get('CERT_DATA_FILE'),
    )
    update('CERT_DATA_FILE', _cert_data_file)
    try:
        with open(_cert_data_file) as file_cert_data:
            _cert_data = yaml.load(file_cert_data.read().decode('utf-8'))
    except IOError:
        _cert_data = {}
    update('CERT_DATA', _cert_data)

update('LOGGING', _log)
