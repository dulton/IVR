# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
import os
import shutil


class FSUploadService(object):
    def __init__(self, fs_path):
        self._fs_path = fs_path

    def uploadHandler(self, project_name, device_login_code, channel_index, data):
        path = os.path.join(self._fs_path, project_name, device_login_code)
        os.makedirs(path, mode=0777)
        with open(os.path.join(path, channel_index+'.jpeg'), 'wb') as f:
            shutil.copyfileobj(data, f)


