# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict


class UserSession(object):
    def __init__(self):
        self._sessions = {}
        """
        {<token>: {''}}
        """