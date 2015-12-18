from ivr.common.exception import IVRError
from ivr.ivt.stream import stream_factory

camera_type_registry = {}


def camera_factory(camera_type, vendor, camera_id, streams, **kwargs):
    if camera_type not in camera_type_registry:
        raise IVRError('Unknown camera type {}'.format(camera_type))
    return camera_type_registry[camera_type](vendor, camera_id, streams, **kwargs)


class MetaCamera(type):
    def __init__(cls, name, bases, dct):
        super(MetaCamera, cls).__init__(name, bases, dct)
        camera_type_registry[cls.type] = cls


class Camera(object):
    __metaclass__ = MetaCamera

    type = 'generic'

    def __init__(self, vendor, camera_id, streams, **kwargs):
        self.vendor = vendor
        self.id = camera_id
        self.streams = {}
        for stream in streams:
            s = stream_factory(stream.pop('type'), self, stream.pop('url'), stream.pop('quality'))
            self.streams[s.type][s.quality] = s

    def __str__(self):
        return '_'.join(self.vendor, self.id)

    def _prepare_stsw_source(self, quality, prefered_type=None):
        if not prefered_type:
            prefered_type = ('rtsp', 'rtmp')

        stream_type = None
        for _type in prefered_type:
            if _type in self.streams:
                stream_type = _type
        for stream_type in self.streams:
            break
        if not stream_type:
            raise IVRError('No possible stream')
        s = self.streams[stream_type][quality]
        s.get_stsw_source()
