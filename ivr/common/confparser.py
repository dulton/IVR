# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division

import yaml
import os

import logging
log = logging.getLogger(__name__)


def parse(file_path):
    if not os.path.isabs(file_path):
        file_path = os.path.join(os.getcwd(), file_path)
    if os.path.isfile(file_path):
        with open(file_path) as f:
            return yaml.load(f)
    else:
        raise Exception("Configure file {0} does not exit".format(file_path))