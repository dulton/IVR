# -*- coding: utf-8 -*-
import time
import gevent

from ivr.common.rpc import RPCSession
from ivr.common.exception import IVRError

import logging
log = logging.getLogger(__name__)


class Camera(object):
    def __init__(self, camera_id, detail):
        self._id = camera_id
        self._detail = detail
        self._detail['id'] = camera_id
        self._streams = detail['streams']
        self._rtp = self._streams[0]['rtp']

    @property
    def id(self):
        return self._id

    @property
    def info(self):
        return self._detail

    def rtmp_publish(self, rtmp_url):
        if rtmp_url in self._streams:
            return
        # TODO create ffmpeg to pull rtp stream and publish it to rtmp_url
        log.info('try to publish rtmp stream from rtp {0} of camera {1}'.format(self._rtp, self._id))
        self._streams = {rtmp_url: {}}

    def rtmp_stop_publish(self, rtmp_url):
        stream = self._streams.pop(rtmp_url, None)
        if stream:
            log.info('Stop publishing to RTMP from rtp {0} of camera {1}'.format(self._rtp, self._id))
            # TODO stop ffmpeg


class IVT(object):
    def __init__(self, ivt_id, cameras):
        self._session = None
        self._cameras = {}
        for camera_id, camera in cameras.iteritems():
            self._cameras[camera_id] = Camera(camera_id, camera)
        self.id = ivt_id

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


