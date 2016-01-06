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

    def get_list(self, project_name, camera_id):
        pass

    def get_by_id(self, stream_id):
        for s in self._streams:
            if s.id == stream_id:
                return s

    def get_stream(self, project_name, camera_id, stream_format, stream_quality):
        for s in self._streams:
            if s.project_name == project_name \
                and s.camera_id == camera_id \
                and s.stream_format == stream_format \
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

    def add_stream(self, *args, **kwargs):
        stream = Stream(*args, **kwargs)
        for s in self._streams:
            if s.id == stream.id:
                raise IVRError('Stream "{0}" alreay exists'.format(stream.id))
        self._streams.append(stream)
        return stream

    def update(self, stream):
        for i, s in enumerate(self._streams):
            if s.id == stream.id:
                self._streams[i] = stream

    def delete(self, stream_id):
        for i, s in enumerate(self._streams):
            if s.id == stream_id:
                self._streams.pop(i)

