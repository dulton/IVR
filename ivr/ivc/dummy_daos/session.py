# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
import time
import gevent
from ivr.common.exception import IVRError
from ivr.ivc.manager.session import UserSession


class UserSession(UserSession):
    pass


class UserSessionDAO(object):

    model_cls = UserSession

    def __init__(self):
        self._sessions = []

    def add_new_user_session(self, *args, **kwargs):
        session = UserSession(*args, **kwargs)
        self._sessions.append(session)
        return session

    def add_user_session(self, session):
        self._sessions.append(session)

    def get_running_count(self, project_name=None, camera_id=None):
        cnt = 0
        for s in self._sessions:
            if (project_name is None or project_name == s.project_name) and (camera_id is None or (camera_id == s.camera_id)):
                cnt += 1
        return cnt

    def get_running_list(self, project_name=None, camera_id=None, start_index=0, max_number=65535):
        session_list = []
        index = 0
        if max_number == 0:
            return session_list
        for s in self._sessions:
            if (project_name is None or project_name == s.project_name) and (camera_id is None or (camera_id == s.camera_id)):
                if index >= start_index:
                    session_list.append(s)
                index += 1
                if index >= start_index+max_number:
                    break
        return session_list

    def get_timeout_list(self, last_keepalive, project_name=None, camera_id=None, max_number=65535):
        session_list = []
        if max_number <= 0:
            return session_list
        for s in self._sessions:
            if (project_name is None or (project_name == s.project_name)) \
                    and (camera_id is None or (camera_id == s.camera_id)) \
                    and (s.end is None and (s.last_keepalive < last_keepalive)):
                session_list.append(s)
                if len(session_list) >= max_number:
                    break
        return session_list

    def get_by_id(self, project_name, session_id):
        for session in self._sessions:
            if session.project_name == project_name and session.session_id == session_id:
                return session

    def update(self, session):
        for i, s in enumerate(self._sessions):
            if s.project_name == session.project_name and s.session_id == session.session_id:
                if session.end is None:
                    self._sessions[i] = session
                else:
                    self._sessions.pop(i)
                return
        raise IVRError("{0} not found".format(session))
