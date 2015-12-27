# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
import gevent
from ivr.common.exception import IVRError
import datetime

class Project(object):

    def __init__(self, name, title="default", desc="", long_desc="",
                 max_media_sessions=0,
                 ctime=None, utime=None):
        self.name = name
        self.title = title
        self.desc = desc
        self.long_desc = long_desc
        self.max_media_sessions = max_media_sessions
        if ctime is None or utime is None:
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

    def __str__(self):
        return 'project "{0}"'.format(self.name)

