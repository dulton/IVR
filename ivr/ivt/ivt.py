# -*- coding: utf-8 -*-
import time
import gevent

from ivr.common.rpc import RPCSession

import logging
log = logging.getLogger(__name__)


class IVT(object):
    def __init__(self, ivt_id):
        self._session = None
        self.id = ivt_id
        gevent.spawn(self.req_echo)

    def ivt_session_factory(self, transport):
        self._session = IVTSession(self, transport)
        return self._session

    def session_closed(self):
        self._session = None



class IVTSession(RPCSession):
    def __init__(self, ivt, transport):
        self._ivt = ivt
        super(IVTSession, self).__init__(transport)

    def on_close(self):
        super(IVTSession, self).on_close()
        self._ivt.session_closed()

    def rpc_getInfo(self):
        return {'id': self._ivt.id}





