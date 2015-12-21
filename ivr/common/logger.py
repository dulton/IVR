# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
import sys
import os
import logging
import logging.handlers
import logging.config


def default_config(debug=False):
    root = logging.getLogger()
    if debug:
        root.setLevel(logging.DEBUG)
    else:
        root.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s [%(process)d] [%(name)s] [%(levelname)s] - %(message)s')
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(formatter)
    root.addHandler(sh)
    program_name = os.path.basename(sys.argv[0])
    rfh = logging.handlers.RotatingFileHandler(os.path.join(os.getcwd(), program_name+'.log'),
                                               maxBytes=10*1024*1024,
                                               backupCount=5)
    rfh.setFormatter(formatter)
    root.addHandler(rfh)

