# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division

class UserSession(object):
    def __init__(self, project_id, camera_uuid, session_id, stream_id):
        self.project_id = project_id
        self.camera_uuid = camera_uuid
        self.session_id = session_id
        self.stream_id = stream_id
        self.format = None
        self.quality = None
        self.start = None
        self.end = None


class UserSessionDAO(object):
    def __init__(self):
        self._sessions = {}

    def add_user_session(self):
        pass

    def get_user_session(self):
        pass

    def update_user_session(self):
        pass