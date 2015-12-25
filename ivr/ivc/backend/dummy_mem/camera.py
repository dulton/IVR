# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
from ivr.ivc.manager.camera import Camera as BaseCamera
from datetime import datetime


class Camera(BaseCamera):
    pass


class CameraDAO(object):
    model_cls = Camera

    def __init__(self):
        self._cameras = [
            Camera(
                uuid='128d4a52-a248-4b5e-b59f-360268cef294',
                device_uuid='335e8ef7-d7d0-4058-b340-f82597b65a1e',
                project_name='weizhong',
                channel_index=1,
                name='camera01',
                is_online=1,
                flags=Camera.FLAG_LD | Camera.FLAG_SD | Camera.FLAG_HD,
                desc='some camera',
                long_desc='',
                longitude=123,
                latitude=234,
                altitude=456,
                ctime=datetime.now(),
                utime=datetime.now()
            ),
            Camera(
                uuid='c72bc4ee-0869-44cc-906d-79bc568d16c6',
                device_uuid='335e8ef7-d7d0-4058-b340-f82597b65a1e',
                project_name='weizhong',
                channel_index=0,
                name='camera02',
                is_online=1,
                flags=Camera.FLAG_LD | Camera.FLAG_SD | Camera.FLAG_HD,
                desc='another camera',
                long_desc='',
                longitude=123,
                latitude=234,
                altitude=456,
                ctime=datetime.now(),
                utime=datetime.now()
            ),
        ]

    def get_camera_count(self, project_name):
        count = 0
        for c in self._cameras:
            if c.project_name == project_name:
                count += 1
        return count

    def get_camera_list(self, project_name, start=0, limit=0):
        result = []
        if limit == 0:
            return result
        for c in self._cameras:
            if len(result) < limit:
                if c.project_name == project_name:
                    result.append(c)
            else:
                break
        return result

    def get_camera(self, project_name, uuid):
        for c in self._cameras:
            if c.uuid == uuid and c.project_name == project_name:
                return c
