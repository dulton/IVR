# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division


class DeviceManager(object):
    def __init__(self, device_dao):
        self._device_dao = device_dao

    def get_device(self, project_id, device_id):
        return self._device_dao.get_device(project_id, device_id)

    def get_device_list(self, project_id, start, limit):
        return self._device_dao.get_device_list(project_id, start, limit)

    def delete_device(self, project_id, device_id):
        return self._device_dao.delete_device(project_id, device_id)

    def update_device(self, device):
        return self._device_dao.update_device(device)

    def rtmp_publish_stream(self, camera_id, quality, publish_url, stream_id):
        pass

    def stop_rtmp_publish(self, camera_id, stream_id):
        pass