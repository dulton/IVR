import time
import gevent
from ivr.common.exception import IVRError

from streamswitch.stream_mngr import create_stream

import logging
log = logging.getLogger(__name__)

stream_type_registry = {}


def stream_factory(stream_type, camera, url, quality, **kwargs):
    if stream_type not in stream_type_registry:
        raise IVRError('Unknown stream type {}'.format(stream_type))
    return stream_type_registry[stream_type](camera, url, quality, **kwargs)


class MetaStream(type):
    def __init__(cls, name, bases, dct):
        super(MetaStream, cls).__init__(name, bases, dct)
        stream_type_registry[cls.type] = cls


class Stream(object):
    __metaclass__ = MetaStream

    type = 'generic'
    stsw_source_type = 'unknown'

    def __init__(self, camera, url, quality, **kwargs):
        self.camera = camera
        self.url = url
        self.quality = quality
        self.stream_name = '_'.join(self.camera.vendor, self.camera.id, self.type, self.quality)
        self.stsw_source = None
        gevent.spawn(self._destroy_stsw_source_on_idle)

    def __str__(self):
        return self.stream_name

    def get_stsw_source(self):
        if not self.stsw_source:
            self.stsw_source = create_stream(source_type=self.stsw_source_type,
                                             stream_name='_'.join(self.stream_name),
                                             url=self.url,
                                             log_file=self.stream_name+'.log')
        return self.stsw_source

    def _destroy_stsw_source_on_idle(self):
        idle_cnt = 0
        while True:
            idle = False
            try:
                time.sleep(30)
                if self.stsw_source:
                    if self.stsw_source.get_client_list(0, 0).total_num == 0:
                        if idle_cnt > 2:
                            self.stsw_source.destroy()
                        else:
                            idle = True
            except Exception:
                log.exception('Failed to check source client')
            finally:
                if idle:
                    idle_cnt += 1
                else:
                    idle_cnt = 0

