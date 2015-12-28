# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
from ivr.ivc.manager.device import Device as DeviceModel
from ivr.common.exception import IVRError
from datetime import datetime


class Device(DeviceModel):
    pass


class DeviceDAO(object):
    model_cls = Device

    def __init__(self):
        self._devices = []

    def get_count_by_project(self, project_name=None):
        cnt = 0
        for d in self._devices:
            if d.project_name == project_name:
               cnt += 1
        return cnt

    def get_list_by_project(self, project_name=None, start_index=0, max_number=65535):
        result = []
        index = 0
        if max_number == 0:
            return result
        for d in self._devices:
            if len(result) < max_number:
                if d.project_name == project_name:
                    if index >= start_index:
                        result.append(d)
                    index += 1
            else:
                break
        return result

    def get_by_uuid(self, device_id):
        for d in self._devices:
            if d.uuid == device_id:
                return d

    def add(self, dev):
        for d in self._devices:
            if d.uuid == dev.uuid:
                raise IVRError('Duplicated device UUID <{0}>'.format(dev.uuid))
        self._devices.append(dev)

    def update(self, device):
        for i, d in enumerate(self._devices):
            if d.project_name == device.project_name and d.uuid == device.uuid:
                self._devices[i] = device
                return
        raise IVRError('No device "{0}" found'.format(device.uuid))

    def delete_by_uuid(self, device_id):
        for i, d in enumerate(self._devices):
            if d.uuid == device_id:
                self._devices.pop(i)
                return

