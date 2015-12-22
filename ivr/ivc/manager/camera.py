# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division

from ivr.common.exception import IVRError

import logging
log = logging.getLogger(__name__)


class Camera(object):
    stream_qualities = ('ld', 'sd', 'hd', 'fhd')
    STATE_OFFLINE = 0
    STATE_ONLINE = 1

    def __init__(self, project_id, uuid, device_uuid, channel_index, name,
                 flags, state, desc, long_desc, longitude, latitude, altitude):
        self.project_id = project_id
        self.uuid = uuid
        self.device_uuid = device_uuid
        self.channel_index = channel_index
        self.flags = flags
        self.state = state
        self.name = name
        self.desc = desc
        self.long_desc = long_desc
        self.longitude = longitude
        self.latitude = latitude
        self.altitude = altitude

    def is_online(self):
        return self.state == self.STATE_ONLINE

    def find_possible_quality(self, stream_quality):
        # find the highest possible quality that lower than or equal to stream_quality
        target = self.stream_qualities[0]
        for i, quality in enumerate(self.stream_qualities):
            if stream_quality == quality and self.flag|(1<<i):
                return quality
            elif stream_quality == quality:
                break
            target = quality
        return target

    def __str__(self):
        return 'camera "{0}" of project "{1}"'.format(self.uuid, self.project_id)


class CameraManager(object):
    def __init__(self, camera_dao, device_mngr):
        self._camera_dao = camera_dao
        self._device_mngr = device_mngr

    def get_camera(self, project, camera_id):
        return self._camera_dao.get_camera(project, camera_id)

    def get_camera_list(self, project, start, limit):
        return self._camera_dao.get_camera_list(project, start, limit)

    def camera_cnt(self, project):
        return self._camera_dao.get_camera_count(project)

    def rtmp_publish_stream(self, project, camera_id, stream_quality, publish_url):
        pass

    def rtmp_stop_publish(self, project, camera_id, publish_url):
        ivt = self._find_ivt(project, camera_id)
        if ivt:
            ivt.stop_rtmp_publish(project, camera_id, publish_url)
        else:
            raise IVRError("'{0}' camera '{1}' does not exist".format(project, camera_id))

    def on_camera_offline(self, camera_id):
        pass

