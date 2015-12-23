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

    def get_stream_list(self, project_name, camera_id):
        pass

    def get_stream_by_id(self, stream_id):
        pass

    def get_stream(self, project_name, camera_id, stream_format, stream_quality):
        for s in self._streams:
            if s.project_name == project_name \
                and s.camera_id == camera_id \
                and s.stream_format == stream_format \
                and s.stream_quality == stream_quality:
                return s

    def add_stream(self, *args, **kwargs):
        stream = Stream(*args, **kwargs)
        for s in self._streams:
            if s.stream_id == stream.stream_id:
                raise IVRError('Stream "{0}" alreay exists'.format(stream.stream_id))
        self._streams.append(stream)
        return stream

    def update_stream(self, stream):
        pass

    def delete_stream(self, stream_id):
        pass