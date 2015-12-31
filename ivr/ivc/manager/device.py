# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
from ivr.common.exception import IVRError
import datetime
import uuid

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
        if ctime is None or utime is None or ltime is None:
            now = datetime.datetime.now()
        else:
            now = 0
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
        return 'device <{0}> of project <{1}>'.format(self.uuid, self.project_name)


class DeviceManager(object):
    def __init__(self, device_dao):
        self._dao = device_dao

    def get_device(self, project_name, device_id):
        device = self._dao.get_by_uuid(device_id)
        if device.project_name != project_name:
            log.warning('Try to access device <{0}> of project <{1}> from project <{1}>'.format(device_id, device.project_name, project_name))
            device = None
        return device

    def get_device_count(self, project_name):
        return self._dao.get_count_by_project(project_name=project_name)

    def get_device_list(self, project_name, start, limit):
        return self._dao.get_list_by_project(project_name=project_name, start_index=start, max_number=limit)

    def add_device(self, project_name, *args, **kwargs):
        device_id = unicode(uuid.uuid4())
        device = Device(project_name, device_id, *args, **kwargs)
        self._dao.add(device)

    def delete_device(self, project_name, device):
        if device.project_name != project_name:
            log.warning('Try to delete device <{0}> of project <{1}> from project <{1}>'.format(device.uuid, device.project_name, project_name))
            return
        return self._dao.delete_by_uuid(project_name, device.uuid)

    def update_device(self, project_name, device):
        if device.project_name != project_name:
            log.warning('Try to update device <{0}> of project <{1}> from project <{1}>'.format(device.uuid, device.project_name, project_name))
            return
        return self._dao.update(device)

    def delete_device_by_id(self, project_name, device_id):
        device = self._dao.get_by_uuid(device_id)
        if device and device.project_name != project_name:
            log.warning('Try to delete device <{0}> of project <{1}> from project <{1}>'.format(device.uuid, device.project_name, project_name))
            return
        elif device:
            self._dao.delete_by_uuid(device.uuid)
        return device

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