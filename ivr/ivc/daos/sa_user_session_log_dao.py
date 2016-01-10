# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
import datetime
from .sa_models import SASessionLog
from ..manager.sessionlog import UserSessionLog


class SAUserSessionLogDao(object):
    def __init__(self, dao_context_mngr):
        self._dao_context_mngr = dao_context_mngr

    def add(self, session_log):
        with self._dao_context_mngr.context() as context:
            # in a transaction
            session = context.session
            sa_session_log = SASessionLog()
            sa_session_log.from_session_log(session_log)
            session.add(sa_session_log)

    def get_by_id(self, uuid):
        with self._dao_context_mngr.context() as context:
            # in a transaction
            session = context.session
            sa_session_log = session.query(SASessionLog).filter(SASessionLog.uuid == uuid).one_or_none()
            if sa_session_log is None:
                return None
            session_log = sa_session_log.to_session_log(UserSessionLog)
        return session_log

    def get_list_by_project(
            self,
            project_name,
            start_from=None,
            end_to=None,
            last_end_time=None,
            last_uuid=None,
            max_number=20):
        if max_number >= 512:
            max_number = 512
        session_log_list = []
        with self._dao_context_mngr.context() as context:
            session = context.session
            query = session.query(SASessionLog)
            query = query.filter(SASessionLog.project_name==project_name)
            if last_end_time:
                query = query.filter(SASessionLog.end >= last_end_time)
            elif start_from:
                query = query.filter(SASessionLog.end >= start_from)
            else:
                query = query.filter(SASessionLog.end >= datetime.datetime(1970, 1, 1))
            if end_to:
                query = query.filter(SASessionLog.end < end_to)
            if last_uuid:
                query = query.filter(SASessionLog.uuid > last_uuid)
            elif last_end_time:
                query = query.filter(SASessionLog.end > last_end_time)
            query = query.order_by(SASessionLog.project_name.desc(), SASessionLog.end.asc(), SASessionLog.uuid.asc()).limit(max_number)
            for sa_session_log in query.all():
                session_log_list.append(sa_session_log.to_session_log(UserSessionLog))
        return session_log_list
