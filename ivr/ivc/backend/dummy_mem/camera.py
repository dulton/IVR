# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
from ivr.common.datatype import VideoQuality


class Camera(object):
    def __init__(self, uuid, device_uuid, project_id, channel_index, name,
                 streams_qualities, desc, longtitude, latitude, altitude):
        self.uuid = uuid
        self.devcie_uuid = device_uuid
        self.project_id = project_id
        self.channel_index = channel_index
        self.name = name
        self.desc = desc
        self.logtitude = longtitude
        self.latitude = latitude
        self.altitude = altitude


class CameraDAO(object):
    def __init__(self):
        self._cameras = [
            Camera(
                uuid='128d4a52-a248-4b5e-b59f-360268cef294',
                device_uuid='335e8ef7-d7d0-4058-b340-f82597b65a1e',
                project_id='weizhong',
                channel_index=1,
                name='camera01',
                streams_qualities=[VideoQuality.HD, VideoQuality.SD, VideoQuality.LD],
                desc='some camera',
                logitude=123,
                latitude=234,
                altitude=456,
            ),
            Camera(
                uuid='c72bc4ee-0869-44cc-906d-79bc568d16c6',
                device_uuid='335e8ef7-d7d0-4058-b340-f82597b65a1e',
                project_id='weizhong',
                channel_index=0,
                name='camera02',
                streams_qualities=[VideoQuality.SD, VideoQuality.LD],
                desc='another camera',
                logitude=123,
                latitude=234,
                altitude=456,
            ),
        ]

    def get_camera_count(self, project_id):
        count = 0
        for c in self._cameras:
            if c.project_id == project_id:
                count += 1
        return count

    def get_camera_list(self, project_id, start=0, limit=0):
        result = []
        if limit == 0:
            return result
        for c in self._cameras:
            if c.project_id == project_id:
                if len(result) < limit:
                    result.append(c)
                    if len(result) + 1 == limit:
                        break
        return result

    def get_camera(self, project_id, uuid):
        for c in self._cameras:
            if c.uuid == uuid and c.project_id == project_id:
                return c
