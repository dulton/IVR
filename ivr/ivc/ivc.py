from ivr.common.rpc import RPCSession

import logging
log = logging.getLogger(__name__)


class IVT(RPCSession):
    def __init__(self, ivt_id, transport=None, encoder=None):
        super(IVT, self).__init__(self, transport)
        self._id = ivt_id

    @property
    def is_online(self):
        return self.closed

    @property
    def id(self):
        return self._id

    def on_close(self):
        super(IVT, self).on_close()
        log.info("{0} disconnected".format(self))
        # TODO info IVC

    def __str__(self):
        return "IVT {0}".format(self._id)


class IVC(object):
    def __init__(self):
        self._ivts = {}

    def ivt_online(self, transport, ivt_id):
        if ivt_id not in self._ivts:
            #log.error("Unkown IVT {0} connected".format(ivt_id))
            #raise Exception("Unknown IVT connected")
            ivt = IVT(ivt_id, transport)
            log.info("New {0} registered".format(ivt))
        else:
            ivt = self._ivts[ivt_id]
            ivt.set_transport(transport)
        return ivt
