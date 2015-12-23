# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
from uuid import uuid4
import gevent
import time
import logging

log = logging.getLogger(__name__)


class UserSession(object):
    def __init__(self, project_id, session_id, camera_id, stream_format, stream_quality, stream_id, url):
        self.project_id = project_id
        self.session_id = session_id
        self.camera_id = camera_id
        self.stream_format = stream_format
        self.stream_quality = stream_quality
        self.stream_id = stream_id
        self.url = url
        self.start = time.time()
        self.end = None
        self.last_keepalive = None

    def __str__(self):
        return '<session "{0}" of project "{1}">'.format(self.session_id, self.project_id)


class UserSessionManager(object):
    def __init__(self, dao, stream_mngr, camera_mngr, ttl):
        self._dao = dao
        self._stream_mngr = stream_mngr
        self._camera_mngr = camera_mngr
        self._ttl = ttl
        gevent.spawn(self._chk_session_ttl)

    def request_session(self, project_id, camera_id, stream_format, stream_quality, create=True):
        stream = self._stream_mngr.request_stream(project_id, camera_id, stream_format, stream_quality, auto_delete=True, create=create)
        session_id = uuid4()
        session = self._dao.add_session(project_id, session_id, camera_id, stream.stream_format, stream.stream_quality, stream.id, stream.url)
        return session.url, session.session_id

    def stop_session(self, project_id, camera_id, session_id):
        session = self._dao.get_user_session(project_id, session_id)
        session.end = time.time()
        self._dao.update_user_session(project_id, session)

    def keepalive_session(self, project_id, camera_id, session_id):
        session = self._dao.get_user_session(project_id, session_id)
        session.last_keepalive = time.time()
        self._dao.update_user_session(project_id, session)

    def _chk_session_ttl(self):
        start = 0
        limit = 20
        while True:
            try:
                now = time.time()
                session_list = self._dao.get_timeout_user_session_list(now-self.ttl, start=start, limit=limit)
                if len(session_list) < limit:
                    start = 0
                else:
                    start += limit
                for s in session_list:
                    s.end = now
                    log.info('{0} timeout'.format(s))
                    self._dao.update_user_session(s.project_id, s)
            except Exception:
                log.exception('Failed to check user session TTL')
                start = 0
            finally:
                gevent.sleep(10)



