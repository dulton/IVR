# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
import gevent
from ivr.common.rpc import RPCSession

import logging
log = logging.getLogger(__name__)


class Device(object):
    STATE_OFFLINE = 0
    STATE_ONLINE = 1

    def __init__(self, project_name, uuid, name="", type="", firmware_model="", hardware_model="",
                 flags=0, is_online=0, desc="", long_desc="", media_channel_num=0,
                 dev_code="", password="", longitude=0.0, latitude=0.0, altitude=0.0):
        self.project_name = project_name
        self.uuid = uuid
        self.name = name
        self.type = type
        self.flags = flags
        self.is_online = is_online
        self.dev_code = dev_code
        self.password = password
        self.firmware_model = firmware_model
        self.hardware_model = hardware_model
        self.media_channel_num = media_channel_num
        self.desc = desc
        self.long_desc = long_desc
        self.longitude = longitude
        self.latitude = latitude
        self.altitude = altitude


class DeviceManager(object):
    def __init__(self, device_dao):
        self._device_dao = device_dao

    def get_device(self, project_name, device_id):
        return self._device_dao.get_device(project_name, device_id)

    def get_device_list(self, project_name, start, limit):
        return self._device_dao.get_device_list(project_name, start, limit)

    def delete_device(self, project_name, device_id):
        return self._device_dao.delete_device(project_name, device_id)

    def update_device(self, device):
        return self._device_dao.update_device(device)

    def rtmp_publish_stream(self, camera_id, quality, publish_url, stream_id):
        pass

    def stop_rtmp_publish(self, camera_id, stream_id):
        pass