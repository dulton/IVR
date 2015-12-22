# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
import gevent
from ivr.common.rpc import RPCSession

import logging
log = logging.getLogger(__name__)


class Device(object):
    STATE_OFFLINE = 0
    STATE_ONLINE = 1

    def __init__(self, project_id, uuid, name, type, firmware_model, hardware_model,
                 flags, state, desc, long_desc, media_channel_num,
                 dev_code, password, longitude, latitude, altitude):
        self.project_id = project_id
        self.uuid = uuid
        self.name = name
        self.type = type
        self.flags = flags
        self.state = state
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