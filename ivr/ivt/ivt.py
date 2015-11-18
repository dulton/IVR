from ivr.common.rpc import RPCSession


class IVT(object):
    def __init__(self):
        self._session = None

    def ivt_session_factory(self, transport):
        self._session = IVTSession(self, transport)


class IVTSession(RPCSession):
    def __init__(self, ivt, transport):
        super(IVTSession, self).__init__(transport)






