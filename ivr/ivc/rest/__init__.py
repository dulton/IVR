# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division

def includeme(config):
    # look into following modules' includeme function
    # in order to register routes
    config.include(__name__ + '.project')
    config.include(__name__ + '.device')
    config.include(__name__ + '.camera')
    config.include(__name__ + '.session')
    config.include(__name__ + '.stream')
    config.include(__name__ + '.user_views')
    config.scan()             # scan to register view callables, must be last statement