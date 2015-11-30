# -*- coding: utf-8 -*-
import gevent
import os
import time

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from ivr.common.rpc import RPCSession
from ivr.common.exception import IVRError

import logging
log = logging.getLogger(__name__)


class IVT(RPCSession):
    def __init__(self, ivt_id, transport=None, encoder=None):
        super(IVT, self).__init__(transport)
        self._id = ivt_id
        self._cameras = OrderedDict()
        gevent.spawn(self._run)

    @property
    def id(self):
        return self._id

    def on_close(self):
        self._cameras = {}
        super(IVT, self).on_close()
        log.info("{0} disconnected".format(self))
        # TODO info IVC

    def force_shutdown(self):
        self._cameras = {}
        super(IVT, self).force_shutdown()

    def __str__(self):
        return "IVT {0}".format(self._id)

    def __len__(self):
        return len(self._cameras)

    def iter_camera(self):
        print 'Cameras'
        for camera in self._cameras.itervalues():
            print camera
            yield camera

    def refresh_info(self):
        if self.is_online:
            info = self._send_request('getInfo')
            # TODO check offline camera
            self._cameras = OrderedDict(info['cameras'])

    def _run(self):
        while True:
            try:
                self.refresh_info()
            except Exception:
                log.exception("Failed to refresh IVT info")
            time.sleep(10)

    def rpc_echo(self, param):
        return param

    def rtmp_publish_stream(self, camera_id, publish_url):
        self._send_request('RTMPPublish', {'camera_id': camera_id,
                                           'url': publish_url,})

    def stop_rtmp_publish(self, camera_id, publish_url):
        self._send_request('RTMPStopPublish', {'camera_id': camera_id,
                                               'url': publish_url})

    def __contains__(self, item):
        return item in self._cameras


class CameraManager(object):
    def __init__(self):
        self._ivts = OrderedDict()

    def ivt_online(self, transport, params):
        if not params.get('id'):
            raise Exception('No IVT ID is given')
        ivt_id = params['id']
        if not ivt_id:
            raise Exception('IVT ID should not be empty')
        if ivt_id not in self._ivts:
            #log.error("Unkown IVT {0} connected".format(ivt_id))
            #raise Exception("Unknown IVT connected")
            ivt = IVT(ivt_id, transport)
            self._ivts[ivt_id] = ivt
            log.info("New {} registered".format(ivt))
        else:
            ivt = self._ivts[ivt_id]
            ivt.set_transport(transport)
        return ivt

    def _find_ivt(self, camera_id):
        for ivt in self._ivts.itervalues():
            if camera_id in ivt:
                return ivt

    def iter_camera(self):
        print 'IVT'
        for ivt in self._ivts.itervalues():
            print ivt
            for camera in ivt.iter_camera():
                yield camera

    def __len__(self):
        total_camera = 0
        print 'IVT total'
        print self._ivts, len(self._ivts)
        for ivt in self._ivts.itervalues():
            print ivt
            total_camera += len(ivt)
        return total_camera

    def rtmp_publish_stream(self, camera_id, publish_url):
        ivt = self._find_ivt(camera_id)
        if ivt:
            ivt.rtmp_publish_stream(camera_id, publish_url)
        else:
            raise IVRError("Camera {0} does not exit".format(camera_id))

    def rtmp_stop_publish(self, camera_id, publish_url):
        ivt = self._find_ivt(camera_id)
        if ivt:
            ivt.stop_rtmp_publish(camera_id, publish_url)
        else:
            raise IVRError("Camera {0} does not exist".format(camera_id))

    def on_camera_offline(self, camera_id):
        pass


class StreamManager(object):
    def __init__(self, camera_mgr, rtmp_publish_url_prefix, stream_ttl=300):
        self._stream_id = 0
        self._streams = {}
        """
        {<camera>: {<format>: {last_keepalive: <>,
                               keepalive_required: <>,
                               url: <>,
                               ready: <>}}}
        """
        self._camera_mgr = camera_mgr
        self._rtmp_publish_url_prefix = rtmp_publish_url_prefix
        self._stream_ttl = stream_ttl

    def get_stream(self, camera_id, stream_format='hls', keepalive_required=False, create=True):
        for _ in xrange(5):
            # if we are already setting up the stream, retry several times,
            # and return to user only when it is finally ready
            if camera_id in self._streams and stream_format in self._streams[camera_id]:
                # stream already exists
                if not keepalive_required:
                    self._streams[camera_id][stream_format]['keepalive_required'] = False
                if not self._streams[camera_id][stream_format]['ready']:
                    time.sleep(1)
                    continue
                return self._streams[camera_id][stream_format]['url']
            elif camera_id in self._streams:
                # no such stream exists
                if create:
                    stream = self._create_stream(camera_id, stream_format, keepalive_required)
                    return stream['url']
                else:
                    raise IVRError('Stream does not exists', 404)
            elif create:
                # try to create stream
                stream = self._create_stream(camera_id, stream_format, keepalive_required)
                return stream['url']
        raise IVRError("Failed to get {0} stream for camera {1}".format(stream_format, camera_id))

    def delete_stream(self, camera_id, stream_format='hls', force=False):
        if camera_id not in self._streams:
            raise IVRError("No such camera {0}".format(camera_id))
        if stream_format not in self._streams[camera_id]:
            raise IVRError("No stream {0} in camera {1}".format(stream_format, camera_id))
        stream = self._streams[camera_id][stream_format]
        if force:
            self._destroy_stream(camera_id, stream_format)
        elif not stream['keepalive_required']:
            self._destroy_stream(camera_id, stream_format)
        else:
            # mark it keepalive required, so when no one is watching, this stream will
            # be deleted automatically
            stream['keepalive_required'] = True

    def keepalive_stream(self, camera_id, stream_format='hls'):
        if camera_id not in self._streams:
            raise IVRError("No such camera {0}".format(camera_id))
        if stream_format not in self._streams[camera_id]:
            raise IVRError("No stream {0} in camera {1}".format(stream_format, camera_id))
        stream = self._streams[camera_id][stream_format]
        stream['last_keepalive'] = time.time()

    def on_camera_offline(self, camera_id):
        pass

    def _next_stream_id(self):
        self._stream_id += 1
        return self._stream_id

    def _create_stream(self, camera_id, stream_format, keepalive_required):
        stream_id = self._next_stream_id()
        if stream_format == 'hls':
            url = 'hls/{0}.m3u8'.format(stream_id)
            stream = {'last_keepalive': time.time(),
                      'keepalive_required': keepalive_required,
                      'ready': False,
                      'url': url,
                      'id': stream_id,}
            if camera_id in self._streams:
                self._streams[camera_id][stream_format] = stream
            else:
                self._streams[camera_id] = {stream_format: stream}
            rtmp_publish_url = os.path.join(self._rtmp_publish_url_prefix, str(stream_id))
            self._camera_mgr.rtmp_publish_stream(camera_id, rtmp_publish_url)
            stream['ready'] = True
            return stream
        else:
            raise IVRError('Unsupported stream format {0}'.format(stream_format))


    def _destroy_stream(self, camera_id, stream_format):
        stream = self._streams[camera_id][stream_format]
        rtmp_publish_url = os.path.join(self._rtmp_publish_url_prefix, str(stream['id']))
        self._camera_mgr.rtmp_stop_publish(camera_id, rtmp_publish_url)

    def _chk_stream_timeout(self):
        while True:
            time.sleep(1)
            try:
                now = time.time()
                for camera_id, streams in self._streams.iteritems():
                    for stream_format, stream in streams.iteritems():
                        if stream['keepalive_required']:
                            if stream['last_keepalive'] + self._stream_ttl < now:
                                self._destroy_stream(camera_id, stream_format)
            except Exception:
                log.exception("Failed to check stream timeout")