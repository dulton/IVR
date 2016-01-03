# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
import uuid
import time
import gevent
from ivr.common.exception import IVRError
from ivr.common.utils import STRING

from streamswitch.stream_mngr import create_stream
from streamswitch.sender_mngr import create_sender
from streamswitch.senders.native_ffmpeg_sender import NATIVE_FFMPEG_SENDER_TYPE_NAME

import logging
log = logging.getLogger(__name__)

stream_type_registry = {}


def stream_factory(stream_type, camera, url, quality, **kwargs):
    if stream_type not in stream_type_registry:
        raise IVRError('Unknown stream type {0}'.format(stream_type))
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
        self.on = False
        self.stream_name = STRING(uuid.uuid4())
        self.stsw_source = None
        self.stsw_senders = {}
        gevent.spawn(self._destroy_stsw_source_on_idle)

    def __str__(self):
        return self.stream_name

    def rtmp_publish(self, rtmp_url):
        self._prepare_stsw_source()
        sender_name = '_'.join(('rtmp', 'sender', self.stream_name))
        sender = create_sender(sender_type=NATIVE_FFMPEG_SENDER_TYPE_NAME,
                               sender_name=sender_name,
                               dest_url=rtmp_url,
                               log_file=sender_name + '.log',
                               dest_format='flv',
                               stream_name=self.stream_name,
                               extra_options={'vcodec': 'copy'})
        self.stsw_senders[NATIVE_FFMPEG_SENDER_TYPE_NAME] = sender
        self.on = True

    def rtmp_stop_publish(self):
        self.on = False
        sender = self.stsw_senders.pop(NATIVE_FFMPEG_SENDER_TYPE_NAME, None)
        if sender:
            sender.destory()

    def _prepare_stsw_source(self):
        if not self.stsw_source:
            self.stsw_source = create_stream(source_type=self.stsw_source_type,
                                             stream_name='_'.join(self.stream_name),
                                             url=self.url,
                                             log_file=self.stream_name+'.log')

    def _destroy_stsw_source_on_idle(self):
        idle_cnt = 0
        while True:
            idle = False
            try:
                time.sleep(30)
                if self.stsw_source:
                    if self.stsw_source.get_client_list(0, 0).total_num == 0:
                        if idle_cnt > 2:
                            # TODO small chance stream session is establishing,
                            # and we may destroy it before sender just about to connect to it
                            self.on = False
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


import pkgutil
for loader, name, is_pkg in pkgutil.walk_packages(__path__):
    loader.find_module(name).load_module(name)
