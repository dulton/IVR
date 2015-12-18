from ivr.common.exception import IVRError
from ivr.ivt.stream import stream_factory

camera_type_registry = {}


def camera_factory(camera_type, tenant, camera_id, streams, **kwargs):
    if camera_type not in camera_type_registry:
        raise IVRError('Unknown camera type {}'.format(camera_type))
    return camera_type_registry[camera_type](tenant, camera_id, streams, **kwargs)


class MetaCamera(type):
    def __init__(cls, name, bases, dct):
        super(MetaCamera, cls).__init__(name, bases, dct)
        camera_type_registry[cls.type] = cls


class Camera(object):
    __metaclass__ = MetaCamera

    type = 'generic'

    def __init__(self, tenant, camera_id, streams, **kwargs):
        self.tenant = tenant
        self.id = camera_id
        self.streams = {}
        for stream in streams:
            s = stream_factory(stream.pop('type'), self, stream.pop('url'), stream.pop('quality'), **stream)
            self.streams[s.type][s.quality] = s

    def __str__(self):
        return '_'.join(self.tenant, self.id)

    def rtmp_publish(self, quality, rtmp_url):
        stream = self._match_stream(quality, prefered_type=['rtsp'])
        stream.rtmp_publish(rtmp_url)

    def rtmp_stop_publish(self, quality, rtmp_url):
        stream = self._match_stream(quality, prefered_type=['rtsp'])
        stream.rtmp_stop_publish()

    def _match_stream(self, quality, prefered_type=None):
        if not prefered_type:
            prefered_type = ('rtsp', 'rtmp')

        stream_type = None
        for _type in prefered_type:
            if _type in self.streams:
                stream_type = _type
        for stream_type in self.streams:
            break
        if not stream_type:
            raise IVRError('No possible stream for "{0}"'.format(self))
        if quality not in self.streams[stream_type]:
            raise IVRError('No proper {0} stream for camera "{1}"'.format(quality, self))
        return self.streams[stream_type][quality]

    def _keepalive(self):
        pass