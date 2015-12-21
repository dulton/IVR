# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
import gevent
from ivr.common.rpc import RPCSession

import logging
log = logging.getLogger(__name__)


class IVT(RPCSession):
    def __init__(self, ivt_id, transport=None, encoder=None):
        super(IVT, self).__init__(transport)
        self._id = ivt_id
        self._cameras = OrderedDict()
        gevent.spawn(self._run)

    @property
    def id(self):
        return self._id

    def on_close(self):
        self._cameras = {}
        super(IVT, self).on_close()
        log.info("{0} disconnected".format(self))
        # TODO info IVC

    def force_shutdown(self):
        self._cameras = {}
        super(IVT, self).force_shutdown()

    def __str__(self):
        return "IVT {0}".format(self._id)

    def __len__(self):
        return len(self._cameras)

    def camera_cnt(self, project):
        return len(self._cameras)

    def iter_camera(self):
        for camera in self._cameras.itervalues():
            yield camera

    def get_camera(self, project, camera_id):
        return self._cameras.get(camera_id)

    def refresh_info(self):
        if self.is_online:
            info = self._send_request('getInfo')
            # TODO check offline camera
            self._cameras = OrderedDict(info['cameras'])

    def _run(self):
        while True:
            try:
                self.refresh_info()
            except Exception:
                log.exception("Failed to refresh IVT info")
            time.sleep(30)

    def rpc_echo(self, param):
        return param

    def rtmp_publish_stream(self, project, camera_id, publish_url):
        self._send_request('RTMPPublish', {'camera_id': camera_id,
                                           'url': publish_url,})

    def stop_rtmp_publish(self, project, camera_id, publish_url):
        self._send_request('RTMPStopPublish', {'camera_id': camera_id,
                                               'url': publish_url})

    def __contains__(self, item):
        return item in self._cameras


class IVTManager(object):
    def __init__(self):
