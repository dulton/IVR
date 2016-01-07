# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
import gevent
import os
import uuid
import time
import datetime

from ivr.common.exception import IVRError
from ivr.common.utils import STRING, wait_util_http_resource_ready
from ivr.common.datatype import VideoQuality

import logging
log = logging.getLogger(__name__)

class Stream(object):

    FLAG_RTMP_READY = 1
    FLAG_HLS_READY = 2

    def __init__(self, project_name, stream_id, camera_id, stream_quality,
                 publish_to, hls_url, rtmp_url, hls_ready=False, rtmp_ready=False,
                 start=None, end=None, last_keepalive=None):
        self.id = stream_id
        self.project_name = project_name
        self.camera_id = camera_id
        self.stream_quality = stream_quality
        self.publish_to = publish_to
        self.hls_url = hls_url
        self.rtmp_url = rtmp_url
        self.hls_ready = False
        self.rtmp_url = False
        if start is None:
            self.start = datetime.datetime.now()
            self.last_keepalive = self.start
            self.end = None
        else:
            self.start = start
            self.end = end
            self.last_keepalive = datetime.datetime.now()

    def __str__(self):
        return '{0} stream {1} of camera {2} project {3}'.format(self.stream_quality, self.id, self.camera_id, self.project_name)


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

    def request_stream(self, project_name, camera_id, stream_format='hls', stream_quality=VideoQuality.LD, auto_delete=True, create=True):
        # TODO concurrent request for the same stream maybe harmful, need to handle this situation
        # find possible existing stream
        stream = self._dao.get_stream(project_name, camera_id, stream_quality)
        if stream:
            return self._wait_util_ready(stream_format, stream)
        camera = self._camera_mngr.get_camera(project_name, camera_id)
        if not camera:
            raise IVRError('No such camera <{0}> or project <{1}>'.format(camera_id, project_name))
        if camera.is_online == camera.STATE_OFFLINE:
            raise IVRError('{0} is offline'.format(camera))
        target_quality = camera.find_possible_quality(stream_quality)
        if target_quality != stream_quality:
            stream = self._dao.get_stream(project_name, camera_id, target_quality)
            if stream:
                return self._wait_util_ready(stream_format, stream)
        # target stream does not exist, create stream
        stream_id = STRING(uuid.uuid4())
        publish_to = os.path.join(self._rtmp_publish_url_prefix, stream_id)
        stream = Stream(
            project_name=project_name,
            stream_id=stream_id,
            camera_id=camera_id,
            stream_quality=stream_quality,
            publish_to=publish_to,
            hls_url=self.calc_url('hls', stream_id),
            rtmp_url=self.calc_url('rtmp', stream_id),
            rtmp_ready=True,
        )
        self._dao.add(stream)
        self._camera_mngr.rtmp_publish_stream(project_name, camera_id, stream_id, target_quality, publish_to)
        try:
            return self._wait_util_ready(stream_format, stream)
        except Exception:
            self._dao.delete(stream_id)
            self._camera_mngr.stop_rtmp_publish(stream_id)
            raise

    def get_stream_count(self, project_name, camera_id):
        return self._dao.get_count(project_name, camera_id)

    def get_stream_list(self, project_name, camera_id, start, limit):
        return self._dao.get_list(project_name, camera_id, start_index=start, max_number=limit)

    def get_stream(self, project_name, camera_id, stream_id):
        stream = self._dao.get_by_id(stream_id)
        if stream and stream.project_name != project_name:
            log.warning('Try to access {0} from project <{1}>'.format(stream, project_name))
            stream = None
        elif stream and stream.camera_id != camera_id:
            log.warning('Try to access {0} from camera <{1}>'.format(stream, camera_id))
            stream = None
        return stream

    def _wait_util_ready(self, stream_format, stream):
        if stream_format == 'hls':
            if stream.hls_ready:
                self._dao.set_keepalive(stream.id, datetime.datetime.now())
                return stream
            elif wait_util_http_resource_ready(stream.hls_url, timeout=5, retry_wait=1, retry=30):
                self._dao.set_hls_ready(stream.id, keepalive=datetime.datetime.now())
                return stream
            else:
                raise IVRError('Failed to create {0}'.format(stream))
        self._dao.set_keepalive(stream.id, datetime.datetime.now())
        return stream

    def stop_stream(self, project_name, camera_id, stream_id):
        stream = self._dao.get_by_id(stream_id)
        if not stream:
            return
        if stream and stream.project_name != project_name:
            log.warning('Try to delete {0} from project <{1}>'.format(stream, project_name))
            return
        elif stream and stream.camera_id != camera_id:
            log.warning('Try to delete {0} from camera <{1}>'.format(stream, camera_id))
            return
        self._dao.delete(stream.id)
        # TODO chance we may fail to request stop publish to IVT
        self._camera_mngr.stop_rtmp_publish(stream.project_name, stream.camera_id, stream.id)
        log.info('Stop {0}'.format(stream))

    def keepalive(self, stream_id):
        stream = self._dao.get_by_id(stream_id)
        if stream:
            stream.last_keepalive = datetime.datetime.now()
            self._dao.update(stream)

    def calc_url(self, stream_format, stream_id):
        if stream_format == 'hls':
            return os.path.join(self._hls_url_prefix, stream_id+".m3u8")
        elif stream_format == 'rtmp':
            return os.path.join(self._rtmp_url_prefix, stream_id)

    def on_camera_offline(self, camera_id):
        pass

    def _del_idle_stream(self):
        while True:
            try:
                last_keepalive = datetime.datetime.now() - datetime.timedelta(seconds=self._stream_ttl)
                streams = self._dao.get_stream_older_than(last_keepalive)
                for stream in streams:
                    self._dao.delete(stream.id)
                    self._camera_mngr.stop_rtmp_publish(stream.project_name, stream.camera_id, stream.id)
                    log.info('Stop {0}'.format(stream))
            except Exception:
                log.exception('Failed to check idle stream')
            finally:
                gevent.sleep(10)