# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
import requests


class UploadClient(object):

    def __init__(self, upload_server, project_name, login_code, login_passwd, channel_index):
        if not upload_server.startswith('http://') and \
                not upload_server.startswith('HTTP://'):
            upload_server = 'http://'+upload_server.strip()
        self._upload_url = upload_server+'api/ivc/v1/projects/{project_name}/devices/{login_code}/channels/{channel_index}/upload_preview'.format(
            project_name=project_name,
            login_code=login_code,
            channel_index=channel_index,
        )
        self._login_code = login_code,
        self._login_passwd = login_passwd

    def upload(self, file_object, content_type=None):
        #headers = {'X-HTTP-IVT-CODE', self._code,
        #          'X-HTTP-IVT-passwd', self._passwd}
        headers = {'Content-Type', content_type or 'image/jpeg'}
        resp = requests.post(self._upload_server, data=file_object, timeout=300, headers=headers)
        resp.raise_for_status()
