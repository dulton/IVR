# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
import datetime
from ivr.common.exception import IVRError

import logging
log = logging.getLogger(__name__)


class UserSessionLog(object):
    def __init__(self, project_name, session_id, key_id, user_ip,
                 camera_id, stream_format, stream_quality,
                 start=None, end=None):
        self.project_name = project_name
        self.session_id = session_id
        self.key_id = key_id
        self.user_ip = user_ip
        self.camera_id = camera_id
        self.stream_format = stream_format
        self.stream_quality = stream_quality,
        if start is None and end is None:
            self.start = datetime.datetime.now()
        else:
            self.start = start
            self.end = end

    def __str__(self):
        return 'user session <{0}> of project <{1}>'.format(self.session_id, self.project_name)

    def is_end(self):
        return self.end is not None


class UserSessionLogManager(object):
    def __init__(self, dao):
        self._dao = dao

    def new_session(self, project_name, session_id, *args, **kwargs):
        session_log = UserSessionLog(project_name, session_id, *args, **kwargs)
        self._dao.add(session_log)

    def session_ends(self, project_name, session_id):
        session_log = self._dao.get_by_id(session_id)
        if not session_log:
            raise IVRError('No session <{0}> found in project <{1}>'.format(session_id, project_name))
        if session_log.project_name != project_name:
            log.warning('Attempt to end {0} from project <{1}>'.format(session_log, project_name))
            return
        if session_log.end is not None:
            return
        session_log.end = datetime.datetime.now()
        self._dao.update(session_log)

    def get_session_log(self, project_name, session_id):
        session_log = self._dao.get_by_id(session_id)
        if not session_log:
            return None
        if session_log.project_name != project_name:
            log.warning('Attempt to get {0} from project <{1}>'.format(session_log, project_name))
            return
        return session_log

    def get_session_log_list(self, project_name, start_from=None, end_to=None, start=0, limit=100):
        return self._dao.get_list_by_project(project_name, start_from=start_from, end_to=end_to, start_index=start, max_number=limit)

    def get_session_log_count(self, project_name, start_from=None, end_to=None, start=0, limit=100):
        return self._dao.get_count_by_project(project_name, start_from=start_from, end_to=end_to)