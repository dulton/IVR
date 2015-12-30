# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
import datetime
import uuid
from ivr.common.exception import IVRError

import logging
log = logging.getLogger(__name__)


class Camera(object):
    stream_qualities = ('ld', 'sd', 'hd', 'fhd')
    STATE_OFFLINE = 0
    STATE_ONLINE = 1
    FLAG_LD = 0b1
    FLAG_SD = 0b10
    FLAG_HD = 0b100

    def __init__(self, project_name, uuid, device_uuid="", channel_index=0, name="cammera",
                 flags=0, is_online=0, desc="", long_desc="", longitude=0.0, latitude=0.0, altitude=0.0, ctime=None, utime=None):
        self.project_name = project_name
        self.uuid = uuid
        self.device_uuid = device_uuid
        self.channel_index = channel_index
        self.flags = flags
        self.is_online = is_online
        self.name = name
        self.desc = desc
        self.long_desc = long_desc
        self.longitude = longitude
        self.latitude = latitude
        self.altitude = altitude
        if ctime is None or utime is None:
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

    def find_possible_quality(self, stream_quality):
        # find the highest possible quality that lower than or equal to stream_quality
        target = self.stream_qualities[0]
        for i, quality in enumerate(self.stream_qualities):
            if stream_quality == quality and self.flags|(1<<i):
                return quality
            elif stream_quality == quality:
                break
            target = quality
        return target

    def __str__(self):
        return 'camera <{0}> of project <{1}>'.format(self.uuid, self.project_name)


class CameraManager(object):
    def __init__(self, camera_dao, device_mngr):
        self._dao = camera_dao
        self._device_mngr = device_mngr

    def get_camera(self, project_name, camera_id):
        camera = self._dao.get_by_uuid(camera_id)
        if camera and camera.project_name != project_name:
            log.warning('Try to access camera <{0}> of project <{1}> from project <{1}>'.format(camera_id, camera.project_name, project_name))
            camera = None
        return camera

    def get_camera_list(self, project_name, start, limit):
        return self._dao.get_list_by_project(project_name=project_name, start_index=start, max_number=limit)

    def get_camera_count(self, project_name):
        return self._dao.get_count_by_project(project_name=project_name)

    def add_camera(self, project_name, **kwargs):
        camera_id = unicode(uuid.uuid4())
        camera = Camera(project_name, camera_id, **kwargs)
        self._dao.add(camera)
        return camera_id

    def delete_camera(self, project_name, camera):
        if project_name != camera.project_name:
            log.warning('Try to delete camera <{0}> of project <{1}> from project <{1}>'.format(camera.uuid, camera.project_name, project_name))
            return
        self._dao.delete_by_uuid(camera.uuid)

    def on_camera_offline(self, camera_id):
        pass

    def rtmp_publish_stream(self, project_name, camera_id, stream_id, target_quality, publish_to):
        camera = self.get_camera(project_name, camera_id)
        self._device_mngr.rtmp_publish_stream(project_name, camera.device_uuid, camera_id, stream_id, target_quality, publish_to)

    def stop_rtmp_publish(self, project_name, camera_id, stream_id):
        camera = self.get_camera(project_name, camera_id)
        self._device_mngr.stop_rtmp_publish(project_name, camera.device_uuid, camera_id, stream_id)

