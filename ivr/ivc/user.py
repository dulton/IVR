# -*- coding: utf-8 -*-

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