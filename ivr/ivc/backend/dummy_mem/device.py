# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
from ivr.ivc.device.model import Device as DeviceModel
from ivr.common.exception import IVRError


class Device(DeviceModel):
    def __init__(self, *args, **kwargs):
        super(Device, self).__init__(*args, **kwargs)


class DeviceDAO(object):
    model_cls = Device

    def __init__(self):
        self._devices = []

    def get_device_count(self, project_id):
        cnt = 0
        for d in self._devices:
            if d.project_id == project_id:
               cnt += 1
        return cnt

    def get_device_list(self, project_id, start, limit):
        result = []
        if limit == 0:
            return result
        for d in self._devices:
            if d.project_id == project_id:
                if len(result) < limit:
                    result.append(d)
                    if len(result) + 1 == limit:
                        break
        return result

    def get_device(self, project_id, device_id):
        for d in self._devices:
            if d.project_id == project_id and d.uuid == device_id:
                return d

    def update_device(self, device):
        for i, d in enumerate(self._devices):
            if d.project_id == device.project_id and d.uuid == device.uuid:
                self._devices[i] = device
                return
        raise IVRError('No device "{0}" found'.format(device.uuid))

    def delete_device(self, project_id, device_id):
        for i, d in enumerate(self._devices):
            if d.project_id == project_id and d.uuid == device_id:
                self._devices.pop(i)
                return

