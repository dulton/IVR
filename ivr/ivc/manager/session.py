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
    def __init__(self, project_name, session_id, camera_id,
                 stream_format, stream_quality, stream_id, url,
                 start=None, end=None,
                 last_keepalive=None, user=''):
        self.project_name = project_name
        self.session_id = session_id
        self.camera_id = camera_id
        self.stream_format = stream_format
        self.stream_quality = stream_quality
        self.stream_id = stream_id
        self.url = url
        if start is None:
            self.start = datetime.datetime.now()
        self.end = end
        if end is None and last_keepalive is None:
            self.last_keepalive = datetime.datetime.now()
        self.user = user

    def __str__(self):
        return 'user session <{0}> of project <{1}>'.format(self.session_id, self.project_name)


class UserSessionManager(object):
    def __init__(self, dao, stream_mngr, ttl):
        self._dao = dao
        self._stream_mngr = stream_mngr
        self._ttl = ttl
        gevent.spawn(self._chk_session_ttl)

    def get_running_session_count(self, project_name, camera_id=None):
        return self._dao.get_running_count(project_name=project_name, camera_id=camera_id)

    def get_running_session_list(self, project_name, camera_id=None, start=0, limit=100):
        return self._dao.get_running_list(project_name=project_name, camera_id=camera_id, start_index=start, max_number=limit)

    def request_session(self, project_name, camera_id, stream_format, stream_quality, user='', create=True):
        stream = self._stream_mngr.request_stream(project_name, camera_id, stream_format, stream_quality, auto_delete=True, create=create)
        session_id = STRING(uuid4())
        session = self._dao.add_new_user_session(
            project_name=project_name,
            session_id=session_id,
            camera_id=camera_id,
            stream_format=stream.stream_format,
            stream_quality=stream.stream_quality,
            stream_id=stream.id,
            url=stream.url,
            user=user,
        )
        log.info('Create {0} for {1}'.format(session, stream))
        return session.url, session_id

    def stop_session(self, project_name, camera_id, session_id):
        session = self._dao.get_by_id(project_name, session_id)
        if not session:
            raise IVRError('session "{0}" of project "{1}" not found'.format(session_id, project_name))
        session.end = time.time()
        self._dao.update(session)
        log.info('Delete {0}'.format(session))

    def keepalive_session(self, project_name, camera_id, session_id):
        session = self._dao.get_by_id(project_name, session_id)
        if not session:
            raise IVRError('session "{0}" of project "{1}" not found'.format(session_id, project_name))
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
                    s.end = now
                    log.info('Timeout {0}'.format(s))
                    self._dao.update(s)
            except Exception:
                log.exception('Failed to check user session TTL')
            finally:
                gevent.sleep(10)



