# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
import gevent
from ivr.common.rpc import RPCSession
from ivr.common.exception import IVRError
import datetime

import logging
log = logging.getLogger(__name__)


class Device(object):
    STATE_OFFLINE = 0
    STATE_ONLINE = 1

    def __init__(self, project_name, uuid, name="device", type="ivt",
                 firmware_model="", hardware_model="",
                 flags=0, is_online=0, desc="", long_desc="",
                 media_channel_num=0,
                 login_code="", login_passwd="",
                 longitude=0.0, latitude=0.0, altitude=0.0,
                 ctime=None, utime=None, ltime=None):
        self.project_name = project_name
        self.uuid = uuid
        self.name = name
        self.type = type
        self.flags = flags
        self.is_online = is_online
        self.login_passwd = login_passwd
        self.is_online = is_online
        if login_code == "":
            self.login_code = uuid
        else:
            self.login_code = login_code
        self.firmware_model = firmware_model
        self.hardware_model = hardware_model
        self.media_channel_num = media_channel_num
        self.desc = desc
        self.long_desc = long_desc
        self.longitude = longitude
        self.latitude = latitude
        self.altitude = altitude
        now = datetime.datetime.now()
        if ctime is None:
            self.ctime = now
        else:
            self.ctime = ctime
        if utime is None:
            self.utime = now
        else:
            self.utime = utime
        if ltime is None:
            self.ltime = now
        else:
            self.ltime = ltime

    def __str__(self):
        return 'device "{0}" of project "{1}"'.format(self.uuid, self.project_name)


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

    def rtmp_publish_stream(self, project_name, device_id, camera_id, stream_id, quality, publish_url):
        pass

    def stop_rtmp_publish(self, project_name, device_id, camera_id, stream_id):
        pass


class DummyDeviceManager(DeviceManager):
    def rtmp_publish_stream(self, project_name, device_id, camera_id, stream_id, quality, publish_url):
        device = self.get_device(project_name, device_id)
        if not device:
            raise IVRError('Device "{0}" of project "{1}" not found'.format(device_id, project_name))
        if not device.is_online:
            raise IVRError('{0} is offline'.format(device))

    def stop_rtmp_publish(self, project_name, device_id, camera_id, stream_id):
        device = self.get_device(project_name, device_id)
        if not device:
            raise IVRError('Device "{0}" of project "{1}" not found'.format(device_id, project_name))
        if not device.is_online:
            raise IVRError('{0} is offline'.format(device))