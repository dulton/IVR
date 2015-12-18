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

    def camera_cnt(self, tenant):
        return len(self._cameras)

    def iter_camera(self):
        for camera in self._cameras.itervalues():
            yield camera

    def get_camera(self, tenant, camera_id):
        return self._cameras.get(camera_id)

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
            time.sleep(30)

    def rpc_echo(self, param):
        return param

    def rtmp_publish_stream(self, tenant, camera_id, publish_url):
        self._send_request('RTMPPublish', {'camera_id': camera_id,
                                           'url': publish_url,})

    def stop_rtmp_publish(self, tenant, camera_id, publish_url):
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
            log.info("New {0} registered".format(ivt))
        else:
            ivt = self._ivts[ivt_id]
            ivt.set_transport(transport)
        return ivt

    def _find_ivt(self, tenant, camera_id):
        for ivt in self._ivts.itervalues():
            if camera_id in ivt:
                return ivt

    def iter_camera(self, tenant):
        for ivt in self._ivts.itervalues():
            for camera in ivt.iter_camera(tenant):
                yield camera

    def get_camera(self, tenant, camera_id):
        ivt = self._find_ivt(tenant, camera_id)
        if not ivt:
            raise IVRError('Camera {0} not found'.format(camera_id))
        camera = ivt.get_camera(camera_id)
        if not camera:
            raise IVRError('Camera {0} not found'.format(camera_id))
        return camera

    def camera_cnt(self, tenant):
        total_camera = 0
        for ivt in self._ivts.itervalues():
            total_camera += ivt.camera_cnt(tenant)
        return total_camera

    def rtmp_publish_stream(self, tenant, camera_id, publish_url):
        ivt = self._find_ivt(tenant, camera_id)
        if ivt:
            ivt.rtmp_publish_stream(tenant, camera_id, publish_url)
        else:
            raise IVRError("{0} camera {1} does not exit".format(tenant, camera_id))

    def rtmp_stop_publish(self, tenant, camera_id, publish_url):
        ivt = self._find_ivt(tenant, camera_id)
        if ivt:
            ivt.stop_rtmp_publish(tenant, camera_id, publish_url)
        else:
            raise IVRError("'{0}' camera '{1}' does not exist".format(tenant, camera_id))

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
        gevent.spawn(self._chk_stream_timeout)

    def get_live_streams(self, tenant, camera_id):
        if camera_id not in self._streams:
            raise IVRError('No live stream found for camera {0}'.format(camera_id))
        return self._streams[camera_id]

    def request_live_stream(self, tenant, camera_id, stream_format='hls', stream_quality='low', keepalive_required=False, create=True):
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
                    stream = self._create_stream(tenant, camera_id, stream_format, keepalive_required)
                    return stream['url']
                else:
                    raise IVRError('Stream does not exists', 404)
            elif create:
                # try to create stream
                stream = self._create_stream(tenant, camera_id, stream_format, keepalive_required)
                return stream['url']
        raise IVRError("Failed to get {0} stream for camera {1}".format(stream_format, camera_id))

    def delete_live_stream(self, tenant, camera_id, session_id=None, force=False):
        if camera_id not in self._streams:
            raise IVRError("No stream {0} from camera {1}".format(stream_format, camera_id))
        if stream_format not in self._streams[camera_id]:
            raise IVRError("No stream {0} from camera {1}".format(stream_format, camera_id))
        stream = self._streams[camera_id][stream_format]
        if force:
            log.info('Force tearing down camera {0} stream {1}'.format(camera_id, stream))
            self._destroy_stream(tenant, camera_id, stream_format)
        else:
            # mark it keepalive required, so when no one is watching, this stream will
            # be deleted automatically
            log.info('Wait for last user leave before tearing down camera {0} stream {1}'.format(camera_id, stream))
            stream['keepalive_required'] = True

    def keepalive_live_stream(self, tenant, camera_id, session_id):
        if camera_id not in self._streams:
            raise IVRError("No stream {0} from camera {1}".format(stream_format, camera_id))
        if stream_format not in self._streams[camera_id]:
            raise IVRError("No stream {0} from camera {1}".format(stream_format, camera_id))
        stream = self._streams[camera_id][stream_format]
        stream['last_keepalive'] = time.time()

    def on_camera_offline(self, camera_id):
        pass

    def _next_stream_id(self):
        self._stream_id += 1
        return self._stream_id

    def _create_stream(self, tenant, camera_id, stream_format, keepalive_required):
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
            self._camera_mgr.rtmp_publish_stream(tenant, camera_id, rtmp_publish_url)
            stream['ready'] = True
            return stream
        else:
            raise IVRError('Unsupported stream format {0}'.format(stream_format))

    def _destroy_stream(self, tenant, camera_id, stream_format):
        stream = self._streams[camera_id].pop(stream_format, None)
        if not stream:
            raise IVRError("No stream {0} from camera {1}".format(stream_format, camera_id))
        if not self._streams[camera_id]:
            self._streams.pop(camera_id, None)
        if stream_format == 'hls':
            rtmp_publish_url = os.path.join(self._rtmp_publish_url_prefix, str(stream['id']))
            self._camera_mgr.rtmp_stop_publish(camera_id, rtmp_publish_url)
        else:
            raise IVRError('Unsupported stream format {0}'.format(stream_format))

    def _chk_stream_timeout(self):
        while True:
            time.sleep(1)
            try:
                now = time.time()
                for camera_id, streams in self._streams.iteritems():
                    for stream_format, stream in streams.iteritems():
                        if stream['keepalive_required']:
                            if stream['last_keepalive'] + self._stream_ttl < now:
                                log.info('camera {0} stream {1} expired, tearing down'.format(camera_id, stream))
                                self._destroy_stream(tenant, camera_id, stream_format)
                                break
                    break
            except Exception:
                log.exception("Failed to check stream timeout")