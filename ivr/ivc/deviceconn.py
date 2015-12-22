# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
import gevent
from ivr.common.rpc import RPCSession

import logging
log = logging.getLogger(__name__)

class DeviceConn(RPCSession):
    pass


class DeviceWSConnectionController(object):
    def __init__(self):
        pass

    def device_online(self, transport, params):
        if not params.get('uuid'):
            raise Exception('No device ID is given')
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