# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division


class UserSession(object):
    def __init__(self, project_id, camera_id, stream_format, stream_quality, stream_id):
        self.project_id = project_id
        self.camera_id = camera_id
        self.stream_format = stream_format
        self.stream_quality = stream_quality
        self.stream_id = stream_id
        self.start = None
        self.end = None
        self.last_keepalive = None


class UserSessionManager(object):
    def __init__(self, dao, stream_mngr, camera_mngr, ttl):
        self._dao = dao
        self._stream_mngr = stream_mngr
        self._camera_mngr = camera_mngr
        self._ttl = ttl

    def request_session(self, project, camera_id, stream_format, stream_quality, create=True):
        pass

    def delete_session(self, project, camera_id, session_id):
        pass

    def keepalive_session(self, project, camera_id, session_id):
        pass

