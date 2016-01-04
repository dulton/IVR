# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
from ivr.common.exception import IVRError
from ivr.ivt.stream import stream_factory
from ivr.common.utils import STRING

camera_type_registry = {}


def camera_factory(camera_type, *args, **kwargs):
    if camera_type not in camera_type_registry:
        raise IVRError('Unknown camera type {0}'.format(camera_type))
    return camera_type_registry[camera_type](*args, **kwargs)


class MetaCamera(type):
    def __init__(cls, name, bases, dct):
        super(MetaCamera, cls).__init__(name, bases, dct)
        camera_type_registry[cls.type] = cls


class Camera(object):
    __metaclass__ = MetaCamera

    STATE_OFFLINE = 0
    STATE_ONLINE = 1
    STATE_BROADCASTING = 2

    type = 'generic'

    def __init__(self, ivt, project_name, channel, streams, **kwargs):
        self._ivt = ivt
        self._project_name = project_name
        self.channel = channel
        self.name = '_'.join((self._ivt.name, STRING(self.channel)))
        self._is_online = self.STATE_ONLINE
        self.streams = {}
        for stream in streams:
            s = stream_factory(stream.pop('type'), self, stream.pop('url'), stream.pop('quality'), **stream)
            if s.type in self.streams:
                self.streams[s.type][s.quality] = s
            else:
                self.streams[s.type] = {s.quality: s}

    def __str__(self):
        return 'camera channel {0} of {1}'.format(self.channel, self._ivt)

    @property
    def is_online(self):
        if self._is_online == self.STATE_OFFLINE:
            return self.STATE_OFFLINE
        else:
            for s in self.iter_streams():
                if s.on:
                    return self.STATE_BROADCASTING
        return self.STATE_ONLINE

    def iter_streams(self):
        for s_list in self.streams.itervalues():
            for s in s_list.itervalues():
                yield s

    def rtmp_publish(self, quality, rtmp_url, stream_id):
        stream = self._match_stream(quality, preferred_type=['rtsp'])
        stream.rtmp_publish(rtmp_url, stream_id)

    def rtmp_stop_publish(self, quality, stream_id):
        stream = self._match_stream(quality, preferred_type=['rtsp'])
        stream.rtmp_stop_publish(stream_id)

    def _match_stream(self, quality, preferred_type=None):
        if not preferred_type:
            preferred_type = ('rtsp', 'rtmp')

        stream_type = None
        for _type in preferred_type:
            if _type in self.streams:
                stream_type = _type
        if stream_type is None:
            for stream_type in self.streams:
                break
        if not stream_type:
            raise IVRError('No possible stream for "{0}"'.format(self))
        if quality not in self.streams[stream_type]:
            raise IVRError('No proper {0} stream for {1}'.format(quality, self))
        return self.streams[stream_type][quality]

    def _keepalive(self):
        pass


import pkgutil
for loader, name, is_pkg in pkgutil.walk_packages(__path__):
    loader.find_module(name).load_module(name)