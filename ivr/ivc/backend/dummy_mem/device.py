# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
from ivr.ivc.manager.device import Device as DeviceModel
from ivr.common.exception import IVRError
from datetime import datetime


class Device(DeviceModel):
    def __init__(self, *args, **kwargs):
        super(Device, self).__init__(*args, **kwargs)


class DeviceDAO(object):
    model_cls = Device

    def __init__(self):
        self._devices = [
            Device(
                project_name='weizhong',
                uuid='335e8ef7-d7d0-4058-b340-f82597b65a1e',
                name='weizhong-device',
                type='IVT',
                firmware_model='f1',
                hardware_model='h1',
                media_channel_num=10,
                is_online=1,
                flags=0,
                login_code='code',
                login_passwd='passwd',
                desc='weizhong device',
                long_desc='',
                longitude=123,
                latitude=456,
                altitude=222,
                ctime=datetime.now(),
                utime=datetime.now(),
                ltime=datetime.now()
            )
        ]

    def get_device_count(self, project_name):
        cnt = 0
        for d in self._devices:
            if d.project_name == project_name:
               cnt += 1
        return cnt

    def get_device_list(self, project_name, start, limit):
        result = []
        index = 0
        if limit == 0:
            return result
        for d in self._devices:
            if len(result) < limit:
                if d.project_name == project_name:
                    if index >= start:
                        result.append(d)
                    index += 1
            else:
                break
        return result

    def get_device(self, project_name, device_id):
        for d in self._devices:
            if d.project_name == project_name and d.uuid == device_id:
                return d

    def update_device(self, device):
        for i, d in enumerate(self._devices):
            if d.project_name == device.project_name and d.uuid == device.uuid:
                self._devices[i] = device
                return
        raise IVRError('No device "{0}" found'.format(device.uuid))

    def delete_device(self, project_name, device_id):
        for i, d in enumerate(self._devices):
            if d.project_name == project_name and d.uuid == device_id:
                self._devices.pop(i)
                return

