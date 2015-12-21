# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
import time
import gevent
from ivr.common.exception import IVRError


class UserSession(object):
    def __init__(self, project_id, camera_uuid, session_id, format, quality):
        self.project_id = project_id
        self.camera_uuid = camera_uuid
        self.session_id = session_id
        self.format = format
        self.quliaty = quality
        self.start = None
        self.end = None

    def __str__(self):
        return "session '{0}' of project '{1}'".format(self.session_id, self.project_id)


class UserSessionDAO(object):

    model_cls = UserSession

    def __init__(self):
        self._sessions = []
        gevent.spawn(self._remove)

    def add_user_session(self, session):
        self._sessions.append(session)

    def get_user_session(self, project_id, session_id):
        for session in self._sessions:
            if session.project_id == project_id and session.session_id == session_id:
                return session

    def update_user_session(self, session):
        for i, s in enumerate(self._sessions):
            if s.project_id == session.project_id and s.session_id == session.session_id:
                if session.end is not None:
                    self._sessions[i] = session
                else:
                    self._sessions.pop(i)
                return
        raise IVRError("{0} not found".format(session))
