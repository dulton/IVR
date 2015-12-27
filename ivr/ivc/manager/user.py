# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
import gevent
from ivr.common.exception import IVRError
import datetime


class User(object):

    def __init__(self, username, password="", title="default", desc="", long_desc="",
                 flags=0, cellphone="", email="",
                 ctime=None, utime=None, ltime=None):
        self.username = username
        self.password = password
        self.title = title
        self.desc = desc
        self.long_desc = long_desc
        self.flags = flags
        self.cellphone = cellphone
        self.email = email
        if ctime is None or utime is None or ltime is None:
            now = datetime.datetime.now()
        else:
            now = 0
        if ctime is None:
            self.ctime = now
        else:
            self.ctime = ctime
        if utime is None:
            self.utime = now
        else:
            self.utime = utime
        if ltime is None:
            self.ltime = now
        else:
            self.ltime = ltime

    def __str__(self):
        return 'User "{0}"'.format(self.username)

