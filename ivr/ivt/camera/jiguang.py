# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
import gevent
import logging
import requests
from requests.auth import HTTPBasicAuth

from ivr.ivt.camera.rtsp import RTSPCamera

log = logging.getLogger(__name__)


class JiguangCamera(RTSPCamera):
    type = 'jiguang'

    def __init__(self, *args, **kwargs):
        self._username = kwargs.pop('username', 'admin')
        self._password = kwargs.pop('passwd', '123456')
        super(JiguangCamera, self).__init__(*args, **kwargs)
        gevent.spawn(self._keepalive)

    def _keepalive(self):
        while True:
            try:
                requests.get(
                    'http://{0}/merlin/GetDeviceInfo.cgi'.format(self._ip),
                    auth=HTTPBasicAuth(self._username, self._password),
                    timeout=10,
                ).raise_for_status()
                if self._is_online == self.STATE_OFFLINE:
                    self._is_online = self.STATE_ONLINE
            except Exception:
                self._is_online = self.STATE_OFFLINE
                log.exception('Failed to keepalive with {0}'.format(self))
                # TODO stop all related source and sender?? and notify IVC
            finally:
                gevent.sleep(10)



