# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
import os
import gevent
import logging
import requests
from requests.auth import HTTPBasicAuth

from ivr.ivt.camera.rtsp import RTSPCamera
from ivr.uploader.client import UploadClient

log = logging.getLogger(__name__)


class JiguangCamera(RTSPCamera):
    type = 'jiguang'

    def __init__(self, *args, **kwargs):
        self._username = kwargs.pop('username', 'admin')
        self._password = kwargs.pop('passwd', '123456')
        self._upload_server = self._ivt.preview_upload_server
        self._upload_interval = kwargs.pop('preview_upload_interval', None)
        super(JiguangCamera, self).__init__(*args, **kwargs)
        gevent.spawn(self._keepalive)
        if self._upload_server and self._upload_interval:
            gevent.spawn(self._upload_preview_image)

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

    def _upload_preview_image(self):
        os.makedirs(os.path.join(os.getcwd(), 'preview_images'), 0755)
        raw_image = os.path.join(os.getcwd(), 'preview_images', self.channel+'_'+self._ip)
        thumbnail = os.path.join(os.getcwd(), 'preview_images', self.channel+'_'+self._ip)
        upload_client = UploadClient(self._upload_server, self._project_name, self._ivt.id, self._ivt.login_passwd, self.channel)
        while True:
            try:
                if self._is_online != self.STATE_OFFLINE:
                    res = requests.get('http://{0}/snapshot_ch=1'.format(self._ip), stream=True)
                    res.raise_for_status()
                    for data in res.iter_content(1024):
                        with open(raw_image, 'wb') as f:
                            f.write(data)
                    # TODO scale image down

                    # upload image to IVC
                    with open(thumbnail, 'rb') as f:
                        upload_client.upload(f)
            except Exception:
                try:
                    res.close()
                except Exception:
                    pass
                log.exception('Failed to fetch or upload preview image of {0}'.format(self))
            finally:
                gevent.sleep(self._upload_interval)


