# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
import time
import gevent

from ivr.common.rpc import RPCSession
from ivr.common.exception import IVRError
from ivr.ivt.camera import camera_factory, Camera

import logging
log = logging.getLogger(__name__)


class IVT(object):
    def __init__(self, project_name, login_code, keepalive_interval, cameras):
        self._project_name = project_name
        self.id = login_code
        self.keepalive_interval = keepalive_interval
        self._session = None
        self._cameras = {}
        for camera in cameras:
            c = camera_factory(camera_type=camera.pop('type'),
                               ivt=self,
                               project_name=project_name,
                               channel=camera.pop('channel'),
                               streams=camera.pop('streams'),
                               **camera)
            self._cameras[c.channel] = c

    def __str__(self):
        return 'IVT <{0}> of project <{1}>'.format(self.id, self._project_name)

    def ivt_session_factory(self, transport):
        self._session = IVTSession(self, transport)
        return self._session

    def session_closed(self):
        self._session = None

    def __contains__(self, item):
        return item in self._cameras

    def iter_cameras(self):
        for c in self._cameras.itervalues():
            yield c

    def cameras_info(self):
        info = {}
        for camera_id, camera in self._cameras.iteritems():
            info[camera_id] = camera.info
        return info

    def rtmp_publish(self, channel, publish_url):
        camera = self._cameras.get(channel)
        if not camera:
            raise IVRError('Channel {0} not exists'.format(channel))
        camera.rtmp_publish(publish_url)

    def rtmp_stop_publish(self, channel, publish_url):
        camera = self._cameras.get(channel)
        if not camera:
            raise IVRError('Channel {0} not exists'.format(channel))
        camera.rtmp_stop_publish(publish_url)


class IVTSession(RPCSession):
    def __init__(self, ivt, transport):
        self._ivt = ivt
        super(IVTSession, self).__init__(transport)
        self._keepalive_greenlet = gevent.spawn(self._keepalive)

    def _keepalive(self):
        while True:
            try:
                data = {}
                for c in self._ivt.iter_cameras:
                    data[c.channel] = {'is_online': c.is_online}
                self._send_event('keepalive', data)
            except Exception:
                log.exception('Failed to send keepalive to IVC')
            finally:
                gevent.sleep(self._ivt.keepalive_interval)

    def on_close(self):
        try:
            gevent.kill(self._keepalive_greenlet)
        except Exception:
            log.exception('Failed to kill keepalive greenlet')
        super(IVTSession, self).on_close()
        self._ivt.session_closed()

    def rpc_getInfo(self):
        return {'id': self._ivt.id, 'cameras': self._ivt.cameras_info()}

    def rpc_RTMPPublish(self, params):
        # TODO schema check
        self._ivt.rtmp_publish(params['camera_id'], params['url'])

    def rpc_RTMPStopPublish(self, params):
        # TODO schema check
        self._ivt.rtmp_stop_publish(params['camera_id'], params['url'])


