# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
import gevent
import os
import time

from ivr.common.exception import IVRError


class Stream(object):
    def __init__(self, project_name, stream_id, camera_id, stream_format, stream_quality, publish_to, url):
        self.id = stream_id
        self.project_name = project_name
        self.camera_id = camera_id
        self.stream_format = stream_format
        self.stream_quality = stream_quality
        self.publish_to = publish_to
        self.url = url
        self.start = time.time()
        self.end = None


class StreamManager(object):
    def __init__(self, dao, camera_mngr, rtmp_publish_url_prefix, rtmp_url_prefix, hls_url_prefix, stream_ttl=300):
        self._dao = dao
        self._stream_id = 0
        self._camera_mngr = camera_mngr
        self._rtmp_publish_url_prefix = rtmp_publish_url_prefix
        self._rtmp_url_prefix = rtmp_url_prefix
        self._hls_url_prefix = hls_url_prefix
        self._stream_ttl = stream_ttl
        gevent.spawn(self._del_idle_stream)

    def request_stream(self, project_name, camera_id, stream_format='hls', stream_quality='low', auto_delete=True, create=True):
        # TODO concurrent request for the same stream maybe harmful, need to handle this situation
        # find possible existing stream
        stream = self._dao.get_stream(project_name, camera_id, stream_format, stream_quality)
        if stream:
            return stream
        camera = self._camera_mngr.get_camera(project_name, camera_id)
        if not camera:
            raise IVRError('No such camera "{0}" or project "{1}"'.format(camera_id, project_name))
        if not camera.is_online:
            raise IVRError('{0} is offline'.format(camera))
        target_quality = camera.find_possible_quality(stream_quality)
        if target_quality != stream_quality:
            stream = self._dao.get_stream(project_name, camera_id, stream_format, target_quality)
            if stream:
                return stream
        # target stream does not exist, create stream
        stream_id = '_'.join((project_name, camera_id, stream_format, stream_quality))
        publish_to = os.path.join(self._rtmp_publish_url_prefix, stream_id)
        url = self.calc_url(stream_format, stream_id)
        stream = self._dao.add_stream(project_name, stream_id, camera_id, stream_format, stream_quality, publish_to, url)
        self._camera_mngr.rtmp_publish_stream(project_name, camera_id, stream_id, target_quality, publish_to)
        return stream

    def stop_stream(self, stream_id):
        pass

    def calc_url(self, stream_format, stream_id):
        if stream_format == 'hls':
            return os.path.join(self._hls_url_prefix, stream_id+".m3u8")
        elif stream_format == 'rtmp':
            return os.path.join(self._rtmp_url_prefix, stream_id)

    def on_camera_offline(self, camera_id):
        pass

    def _del_idle_stream(self):
        pass