# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
import time
import gevent
from gevent.lock import RLock
from ivr.common.exception import IVRError

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
        self._stsw_stream_name = '_'.join((self.camera.name, self.type, self.quality))
        self.stsw_source = None
        self.stsw_senders = {}  # {<sender_type>: {<stream_id>: sender}}
        self._mutex = RLock()
        gevent.spawn(self._destroy_stsw_source_on_idle)

    def __str__(self):
        return '{0} {1} stream of {2}'.format(self.quality, self.type, self.camera)

    def is_source_of(self, stream_id):
        for _, senders in self.stsw_senders.iteritems():
            if stream_id in senders:
                return True
        return False

    def rtmp_publish(self, rtmp_url, stream_id):
        with self._mutex:
            self._create_stsw_rtmp_sender(rtmp_url, stream_id)
            try:
                self._prepare_stsw_source()
            except Exception:
                self._destroy_stsw_rtmp_sender(stream_id)
                raise

    def _create_stsw_rtmp_sender(self, rtmp_url, stream_id):
        # should be protected by mutex
        if NATIVE_FFMPEG_SENDER_TYPE_NAME in self.stsw_senders:
            if stream_id in self.stsw_senders[NATIVE_FFMPEG_SENDER_TYPE_NAME]:
                log.warn('RTMP sender {0} for {1} already exits'.format(stream_id, self))
                return
        sender_name = '_'.join(('rtmp', 'sender', self._stsw_stream_name))
        sender = create_sender(
            sender_type=NATIVE_FFMPEG_SENDER_TYPE_NAME,
            sender_name=sender_name,
            dest_url=rtmp_url,
            log_file='sender_' + sender_name + '.log',
            dest_format='flv',
            stream_name=self._stsw_stream_name,
            extra_options={
                'vcodec': 'copy',
                'acodec': 'aac',
                'ar': '8000',
                'strict': '-2',
                'ac': '1',
                'b:a': '10k',
            })
        if NATIVE_FFMPEG_SENDER_TYPE_NAME in self.stsw_senders:
            self.stsw_senders[NATIVE_FFMPEG_SENDER_TYPE_NAME][stream_id] = sender
        else:
            self.stsw_senders[NATIVE_FFMPEG_SENDER_TYPE_NAME] = {stream_id: sender}
        log.info('Created RTMP sender {0} for {1}'.format(stream_id, self))

    def _destroy_stsw_rtmp_sender(self, stream_id):
        # should be protected by mutex
        if NATIVE_FFMPEG_SENDER_TYPE_NAME in self.stsw_senders:
            sender = self.stsw_senders[NATIVE_FFMPEG_SENDER_TYPE_NAME].pop(stream_id, None)
            if sender:
                sender.destroy()
                log.info('Destroyed RTMP sender {0} for {1}'.format(stream_id, self))
                return
        log.warning('Unable to destroy, RTMP sender {0} for {1} not exists'.format(stream_id, self))

    def _prepare_stsw_source(self):
        # should be protected by mutex
        if not self.stsw_source:
            self.stsw_source = create_stream(source_type=self.stsw_source_type,
                                             stream_name=self._stsw_stream_name,
                                             url=self.url,
                                             log_file='source_' + self._stsw_stream_name + '.log')
            log.info('created STSW source for {0}'.format(self))

    def rtmp_stop_publish(self, stream_id):
        with self._mutex:
            self._destroy_stsw_rtmp_sender(stream_id)

    def _destroy_stsw_source_on_idle(self):
        idle_cnt = 0
        while True:
            idle = False
            try:
                time.sleep(30)
                with self._mutex:
                    if self.stsw_source:
                        if self.stsw_source.get_client_list(0, 0).total_num == 0:
                            if idle_cnt > 2:
                                self.on = False
                                self.stsw_source.destroy()
                                self.stsw_source = None
                                log.info('Destroyed idle STSW source for {0}'.format(self))
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
