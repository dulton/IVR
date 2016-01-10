# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
from uuid import uuid4
import gevent
import time
import datetime
import logging
from ivr.common.exception import IVRError
from ivr.common.utils import STRING

log = logging.getLogger(__name__)


class UserSession(object):
    def __init__(self, project_name, uuid, camera_uuid,
                 stream_format, stream_quality, stream_id, url,
                 start=None, end=None, last_keepalive=None,
                 ip='', user_agent='',
                 username='', subuser=''):
        self.project_name = project_name
        self.uuid = uuid
        self.camera_uuid = camera_uuid
        self.stream_format = stream_format
        self.stream_quality = stream_quality
        self.stream_id = stream_id
        self.url = url
        if start is None:
            self.start = datetime.datetime.now()
        self.end = end
        if end is None and last_keepalive is None:
            self.last_keepalive = datetime.datetime.now()
        self.ip = ip
        self.username = username
        self.subuser = subuser
        self.user_agent = user_agent

    def __str__(self):
        return 'user session <{0}> of project <{1}>'.format(self.uuid, self.project_name)


class UserSessionManager(object):
    def __init__(self, dao, stream_mngr, user_session_log_mngr, ttl):
        self._dao = dao
        self._stream_mngr = stream_mngr
        self._user_session_log_mngr = user_session_log_mngr
        self._ttl = ttl
        gevent.spawn(self._chk_session_ttl)

    def get_running_session_count(self, project_name, camera_id=None):
        return self._dao.get_running_count(project_name=project_name, camera_uuid=camera_id)

    def get_running_session_list(self, project_name, camera_id=None, start=0, limit=100):
        return self._dao.get_running_list(project_name=project_name, camera_uuid=camera_id, start_index=start, max_number=limit)

    def request_session(self, project_name, camera_id, stream_format, stream_quality, create=True,
                        ip='', user_agent='', username='', subuser=''):
        stream = self._stream_mngr.request_stream(project_name, camera_id, stream_format, stream_quality, auto_delete=True, create=create)
        session_id = STRING(uuid4())
        if stream_format == 'hls':
            url = stream.hls_url
        else:
            url = stream.rtmp_url
        session = self._dao.add_new_user_session(
            project_name=project_name,
            uuid=session_id,
            camera_uuid=camera_id,
            stream_format=stream_format,
            stream_quality=stream.stream_quality,
            stream_id=stream.id,
            url=url,
            ip=ip,
            user_agent=user_agent,
            username=username,
            subuser=subuser,
        )
        log.info('Created {0} for {1}'.format(session, stream))
        return session.url, session_id

    def stop_session(self, project_name, camera_id, session_id):
        session = self._dao.get_by_id(project_name, session_id)
        if not session:
            raise IVRError('session <{0}> of project <{1}> not found'.format(session_id, project_name))
        self._stop_session(session)

    def keepalive_session(self, project_name, camera_id, session_id):
        session = self._dao.get_by_id(project_name, session_id)
        if not session:
            raise IVRError('session <{0}> of project <{1}> not found'.format(session_id, project_name))
        session.last_keepalive = datetime.datetime.now()
        self._dao.update(session)
        self._stream_mngr.keepalive(session.stream_id)

    def _chk_session_ttl(self):
        limit = 20
        while True:
            try:
                now = datetime.datetime.now()
                session_list = self._dao.get_timeout_list(now-datetime.timedelta(seconds=self._ttl), max_number=limit)
                for s in session_list:
                    self._stop_session(s, now=now)
            except Exception:
                log.exception('Failed to check user session TTL')
            finally:
                gevent.sleep(10)

    def _stop_session(self, session, now=None):
        if now:
            session.end = now
        else:
            session.end = datetime.datetime.now()
        self._user_session_log_mngr.add_session_log(
            project_name=session.project_name,
            session_id=session.uuid,
            start=session.start,
            end=session.end,
            camera_uuid=session.camera_uuid,
            stream_format=session.stream_format,
            stream_quality=session.stream_quality,
            ip=session.ip,
            user_agent=session.user_agent,
            username=session.username,
            subuser=session.subuser,
        )
        self._dao.update(session)
        log.info('Stopped {0}'.format(session))



