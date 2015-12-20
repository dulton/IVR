import gevent

from ivr.common.exception import IVRError


class StreamManager(object):
    def __init__(self, camera_mngr, rtmp_publish_url_prefix, stream_ttl=300):
        self._stream_id = 0
        self._streams = {}
        """
        {<camera>: {<format>: {last_keepalive: <>,
                               keepalive_required: <>,
                               url: <>,
                               ready: <>}}}
        """
        self._camera_mngr = camera_mngr
        self._rtmp_publish_url_prefix = rtmp_publish_url_prefix
        self._stream_ttl = stream_ttl
        gevent.spawn(self._chk_stream_timeout)

    def get_live_streams(self, project, camera_id):
        if camera_id not in self._streams:
            raise IVRError('No live stream found for camera {0}'.format(camera_id))
        return self._streams[camera_id]

    def request_live_stream(self, project, camera_id, stream_format='hls', stream_quality='low', keepalive_required=False, create=True):
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
                    stream = self._create_stream(project, camera_id, stream_format, keepalive_required)
                    return stream['url']
                else:
                    raise IVRError('Stream does not exists', 404)
            elif create:
                # try to create stream
                stream = self._create_stream(project, camera_id, stream_format, keepalive_required)
                return stream['url']
        raise IVRError("Failed to get {0} stream for camera {1}".format(stream_format, camera_id))

    def delete_live_stream(self, project, camera_id, session_id=None, force=False):
        if camera_id not in self._streams:
            raise IVRError("No stream {0} from camera {1}".format(stream_format, camera_id))
        if stream_format not in self._streams[camera_id]:
            raise IVRError("No stream {0} from camera {1}".format(stream_format, camera_id))
        stream = self._streams[camera_id][stream_format]
        if force:
            log.info('Force tearing down camera {0} stream {1}'.format(camera_id, stream))
            self._destroy_stream(project, camera_id, stream_format)
        else:
            # mark it keepalive required, so when no one is watching, this stream will
            # be deleted automatically
            log.info('Wait for last user leave before tearing down camera {0} stream {1}'.format(camera_id, stream))
            stream['keepalive_required'] = True

    def keepalive_live_stream(self, project, camera_id, session_id):
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

    def _create_stream(self, project, camera_id, stream_format, keepalive_required):
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
            self._camera_mngr.rtmp_publish_stream(project, camera_id, rtmp_publish_url)
            stream['ready'] = True
            return stream
        else:
            raise IVRError('Unsupported stream format {0}'.format(stream_format))

    def _destroy_stream(self, project, camera_id, stream_format):
        stream = self._streams[camera_id].pop(stream_format, None)
        if not stream:
            raise IVRError("No stream {0} from camera {1}".format(stream_format, camera_id))
        if not self._streams[camera_id]:
            self._streams.pop(camera_id, None)
        if stream_format == 'hls':
            rtmp_publish_url = os.path.join(self._rtmp_publish_url_prefix, str(stream['id']))
            self._camera_mngr.rtmp_stop_publish(camera_id, rtmp_publish_url)
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
                                self._destroy_stream(project, camera_id, stream_format)
                                break
                    break
            except Exception:
                log.exception("Failed to check stream timeout")