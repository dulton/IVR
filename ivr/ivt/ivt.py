from ws4py.client.geventclient import WebSocketBaseClient


class wsClient(WebSocketBaseClient):
    def received_message(self, message):
        pass


class IVT(object):
    def __init__(self, ivc):
        self._ivc = ivc



if __name__ == '__main__':
    import gevent.monkey
    gevent.monkey.patch_all()
