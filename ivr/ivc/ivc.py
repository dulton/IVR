# -*- coding: utf-8 -*-
import gevent
import time
import urlparse

from ivr.common.rpc import RPCSession

import logging
log = logging.getLogger(__name__)


class IVT(RPCSession):
    def __init__(self, ivt_id, transport=None, encoder=None):
        super(IVT, self).__init__(transport)
        self._id = ivt_id
        gevent.spawn(self._run)

    @property
    def id(self):
        return self._id

    def on_close(self):
        super(IVT, self).on_close()
        log.info("{0} disconnected".format(self))
        # TODO info IVC

    def __str__(self):
        return "IVT {0}".format(self._id)

    def refresh_info(self):
        if self.is_online:
            log.info('info: {0}'.format(self._send_request('getInfo')))

    def _run(self):
        while True:
            time.sleep(2)
            self.refresh_info()

    def rpc_echo(self, param):
        return param

    def get_stream(self, stream_id):
        pass


class IVC(object):
    def __init__(self):
        self._ivts = {}
        self.stream_sessions = {}
        """
        {<camera>: {<stream>: {<protocol>: {last_keepalive: <>, }}}}
        """

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
            log.info("New {} registered".format(ivt))
        else:
            ivt = self._ivts[ivt_id]
            ivt.set_transport(transport)
        return ivt

    def get_stream(self, camera_id, stream_id, protocol='hls', keepalive_required=False, create=True):
        pass
        # find corresponding ivt session and ask for stream
        # ask nginx-rtmp to

    def delete_stream(self, camera_id, stream_id, protocol='hls', force=False):
        pass

    def keepalive_stream(self, camera_id, stream_id, protocol='hls'):
        pass