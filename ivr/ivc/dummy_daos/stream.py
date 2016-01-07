# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
from ivr.ivc.manager.stream import Stream as BaseStream

from ivr.common.exception import IVRError


class Stream(BaseStream):
    pass


class StreamDAO(object):
    model_cls = Stream

    def __init__(self):
        self._streams = []

    def get_list(self, project_name, camera_id, start_index=0, max_number=65535):
        result = []
        index = 0
        if max_number == 0:
            return result
        for s in self._streams:
            if len(result) < max_number:
                if s.project_name == project_name and s.camera_id == camera_id:
                    if index >= start_index:
                        result.append(s)
                    index += 1
            else:
                break
        return result

    def get_count(self, project_name, camera_id):
        count = 0
        for s in self._streams:
            if s.project_name == project_name and s.camera_id == camera_id:
                count += 1
        return count

    def get_by_id(self, stream_id):
        for s in self._streams:
            if s.id == stream_id:
                return s

    def get_stream(self, project_name, camera_id, stream_quality):
        for s in self._streams:
            if s.project_name == project_name \
                and s.camera_id == camera_id \
                and s.stream_quality == stream_quality:
                return s

    def get_stream_older_than(self, time_threshold, max=10):
        streams = []
        for s in self._streams:
            if len(streams) >= max:
                return streams
            elif s.last_keepalive < time_threshold:
                streams.append(s)
        return streams

    def add(self, stream):
        for s in self._streams:
            if s.id == stream.id:
                raise IVRError('Stream "{0}" alreay exists'.format(stream.id))
        self._streams.append(stream)
        return stream

    def update(self, stream):
        for i, s in enumerate(self._streams):
            if s.id == stream.id:
                self._streams[i] = stream

    def set_keepalive(self, stream_id, keepalive):
        for s in self._streams:
            if s.id == stream_id:
                s.last_keepalive = keepalive

    def set_rtmp_ready(self, stream_id, keepalive=None):
        for s in self._streams:
            if s.id == stream_id:
                s.rtmp_ready = True
                if keepalive:
                    s.last_keepalive = keepalive

    def set_hls_ready(self, stream_id, keepalive=None):
        for s in self._streams:
            if s.id == stream_id:
                s.hls_ready = True
                if keepalive:
                    s.last_keepalive = keepalive

    def delete(self, stream_id):
        for i, s in enumerate(self._streams):
            if s.id == stream_id:
                self._streams.pop(i)

