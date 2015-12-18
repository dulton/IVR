# -*- coding: utf-8 -*-
import time
import gevent

from ivr.common.rpc import RPCSession
from ivr.common.exception import IVRError
from ivr.ivt.camera import camera_factory

import logging
log = logging.getLogger(__name__)


class IVT(object):
    def __init__(self, ivt_id, cameras):
        self.id = ivt_id
        self._session = None
        self._cameras = {}
        for camera in cameras:
            tenant = camera.pop('tenant')
            camera_id = camera.pop('id')
            c = camera_factory(camera_type=camera.pop('type'),
                               tenant=tenant,
                               camera_id=camera_id,
                               streams=camera.pop('streams'),
                               **camera)
            if tenant not in self._cameras:
                self._cameras[tenant] = {camera_id: c}
            else:
                self._cameras[tenant][camera_id] = c

    def ivt_session_factory(self, transport):
        self._session = IVTSession(self, transport)
        return self._session

    def session_closed(self):
        self._session = None

    def __contains__(self, item):
        return item in self._cameras

    def cameras_info(self):
        info = {}
        for camera_id, camera in self._cameras.iteritems():
            info[camera_id] = camera.info
        return info

    def rtmp_publish(self, camera_id, publish_url):
        camera = self._cameras.get(camera_id)
        if not camera:
            raise IVRError('No such camera {0}'.format(camera_id))
        camera.rtmp_publish(publish_url)

    def rtmp_stop_publish(self, camera_id, publish_url):
        camera = self._cameras.get(camera_id)
        if not camera:
            raise IVRError('No such camera {0}'.format(camera_id))
        camera.rtmp_stop_publish(publish_url)


class IVTSession(RPCSession):
    def __init__(self, ivt, transport):
        self._ivt = ivt
        super(IVTSession, self).__init__(transport)

    def on_close(self):
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


