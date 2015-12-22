# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division

from ivr.common.exception import IVRError

import logging
log = logging.getLogger(__name__)


class Camera(object):
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


class CameraManager(object):
    def __init__(self, camera_dao):
        self._camera_dao = camera_dao

    def ivt_online(self, transport, params):
        if not params.get('id'):
            raise Exception('No IVT ID is given')
        ivt_id = params['id']
        if not ivt_id:
            raise Exception('IVT ID should not be empty')
        if ivt_id not in self._ivts:
            #log.error("Unkown IVT {0} connected".format(ivt_id))
            #raise Exception("Unknown IVT connected")
            ivt = IVT(ivt_id, transport)
            self._ivts[ivt_id] = ivt
            log.info("New {0} registered".format(ivt))
        else:
            ivt = self._ivts[ivt_id]
            ivt.set_transport(transport)
        return ivt

    def _find_ivt(self, project, camera_id):
        for ivt in self._ivts.itervalues():
            if camera_id in ivt:
                return ivt

    def get_camera(self, project, camera_id):
        return self._camera_dao.get_camera(project, camera_id)

    def get_camera_list(self, project, start, limit):
        return self._camera_dao.get_camera_list(project, start, limit)

    def camera_cnt(self, project):
        return self._camera_dao.get_camera_count(project)

    def rtmp_publish_stream(self, project, camera_id, publish_url):
        ivt = self._find_ivt(project, camera_id)
        if ivt:
            ivt.rtmp_publish_stream(project, camera_id, publish_url)
        else:
            raise IVRError("{0} camera {1} does not exit".format(project, camera_id))

    def rtmp_stop_publish(self, project, camera_id, publish_url):
        ivt = self._find_ivt(project, camera_id)
        if ivt:
            ivt.stop_rtmp_publish(project, camera_id, publish_url)
        else:
            raise IVRError("'{0}' camera '{1}' does not exist".format(project, camera_id))

    def on_camera_offline(self, camera_id):
        pass

