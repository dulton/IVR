# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division

def includeme(config):
    # look into following modules' includeme function
    # in order to register routes
    config.include(__name__ + '.camera')
    config.include(__name__ + '.session')
    config.include(__name__ + '.stream')
    config.scan()             # scan to register view callables, must be last statement