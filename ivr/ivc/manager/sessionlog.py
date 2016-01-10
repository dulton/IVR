# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
import datetime
from ivr.common.exception import IVRError

import logging
log = logging.getLogger(__name__)


class UserSessionLog(object):
    def __init__(self, project_name, uuid, start, end,
                 camera_uuid, stream_format, stream_quality,
                 ip, user_agent, username=None, subuser=None):
        self.project_name = project_name
        self.uuid = uuid
        self.start = start
        self.end = end
        self.camera_uuid = camera_uuid
        self.stream_format = stream_format
        self.stream_quality = stream_quality
        self.ip = ip
        self.user_agent = user_agent
        self.username = username  # username in IVR system related to authentication
        self.subuser = subuser  # user name given in request from client

    def __str__(self):
        return 'user session <{0}> of project <{1}>'.format(self.uuid, self.project_name)

    def is_end(self):
        return self.end is not None


class UserSessionLogManager(object):
    """
    Session log is for billing purpose, so no update, no delete
    for performance reason, no count API
    """
    def __init__(self, dao):
        self._dao = dao

    def add_session_log(self, project_name, session_id, *args, **kwargs):
        # TODO validation?
        session_log = UserSessionLog(project_name, session_id, *args, **kwargs)
        self._dao.add(session_log)

    def get_session_log(self, project_name, session_id):
        session_log = self._dao.get_by_id(session_id)
        if not session_log:
            return None
        if session_log.project_name != project_name:
            log.warning('Attempt to get {0} from project <{1}>'.format(session_log, project_name))
            return
        return session_log

    def get_session_log_list(self, project_name, start_from=None, end_to=None, last_end_time=None, last_session_id=None, limit=20):
        return self._dao.get_list_by_project(
            project_name,
            start_from=start_from,
            end_to=end_to,
            last_end_time=last_end_time,
            last_uuid=last_session_id,
            max_number=limit,
        )
