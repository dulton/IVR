# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division


class UserSessionManager(object):
    def __init__(self, dao, stream_mngr, ttl):
        self._dao = dao
        self._stream_mngr = stream_mngr
        self._ttl = ttl

    def request_session(self, project, camera_id, format, quality, create=True):
        pass

    def delete_session(self, project, camera_id, session_id):
        pass

    def keepalive_session(self, project, camera_id, session_id):
        pass