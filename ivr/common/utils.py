# -*- coding: utf-8 -*-
"""
ivr.common.utils
~~~~~~~~~~~~~~~~

This module provide some utils function for IVR

:copyright: (c) 2015 by OpenSight (www.opensight.cn).
:license: AGPLv3, see LICENSE for more details.

"""
from __future__ import unicode_literals, division
import json
import sys
import shutil
import functools
import base64
import datetime
import requests
import time


if sys.version_info[:2] < (3, 3):
    from distutils.spawn import find_executable
else:
    def find_executable(name):
        return shutil.which(name)

if sys.version_info[:1] < (3, ):
    STRING = unicode
else:
    STRING = str


class CustomJSONEncoder(json.JSONEncoder):
    def __init__(self, *args, **kwargs):
        # dirty hack to keep 'default' method intact
        kwargs.pop('default', None)
        super(CustomJSONEncoder, self).__init__(*args, **kwargs)

    def default(self, o):

        # print(o)
        # change bytes to base64 string(unicode for python2, str for python3)
        if isinstance(o, bytes):
            o = base64.b64encode(o).decode()
            return o
        elif isinstance(o, datetime.datetime):
            return STRING(o.strftime('%Y-%m-%dT%H:%M:%S'))
        elif isinstance(o, set):
            return list(o)
        elif hasattr(o, '__json__'):
            return o.__json__()
        elif hasattr(o, '__dict__'):
            obj_dict = {}
            for k, v in o.__dict__.items():
                if not k.startswith('_'):
                    obj_dict[k] = v
            return obj_dict
        else:
            return json.JSONEncoder.default(self, o)


def encode_json(o):
    return json.dumps(o, check_circular=True, cls=CustomJSONEncoder)


def is_str(s):
    if sys.version_info[:1] < (3, ):
        isinstance(s, unicode)
    else:
        isinstance(s, str)


def import_method(path):

    if ":" in path:
        # some.module:some.attribute format
        module_path, dummy_sep, attr_path = path.partition(":")
        module = __import__(module_path, fromlist=['__name__'], level=0)
        attrs = attr_path.split('.')
    else:
        # some.module.some.attribute format
        parts = path.split('.')
        module = None
        parts_copy = parts[:]
        while parts_copy:
            try:
                module = __import__('.'.join(parts_copy))
                break
            except ImportError:
                del parts_copy[-1]
                if not parts_copy:
                    raise
        attrs = parts[1:]

    return functools.reduce(getattr, attrs, module)


def wait_util_http_resource_ready(url, timeout=5, retry_wait=5, retry=0):
    while retry >= 0:
        try:
            status_code = requests.head(url, timeout=timeout).status_code
            if status_code == 200:
                return True
            elif status_code == 404:
                retry -= 1
                time.sleep(retry_wait)
                continue
            else:
                return False
        except Exception:
            return False
