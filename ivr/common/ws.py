import gevent
from gevent.lock import RLock
from ws4py.server.geventserver import WSGIServer
from ws4py.server.wsgiutils import WebSocketWSGIApplication
from ws4py.websocket import WebSocket
from ws4py.client.geventclient import WebSocketClient


class WSClientTransport(WebSocketClient):

    def __init__(self, *args, **kwargs):
        # patch socket.sendall to protect it with lock,
        # in order to prevent sending data from multiple greenlets concurrently
        WebSocketClient.__init__(self, *args, **kwargs)
        self._lock = RLock()
        _sendall = self.sock.sendall

        def sendall(self, data):
            self._lock.acquire()
            try:
                _sendall(self, data)
            except:
                raise
            finally:
                self._lock.release()
        self.sock.sendall = sendall

    def closed(self, code, reason=None):
        pass

    def ponged(self, pong):
        pass


class WSServerTransport(WebSocket):
    APP = None

    def opened(self):
        # patch socket.sendall to protect it with lock,
        # in order to prevent sending data from multiple greenlets concurrently
        self._lock = RLock()
        _sendall = self.sock.sendall

        def sendall(self, data):
            self._lock.acquire()
            try:
                _sendall(self, data)
            except:
                raise
            finally:
                self._lock.release()
        self.sock.sendall = sendall

    def closed(self, code, reason=None):
        pass

    def ponged(self, pong):
        pass

    def received_message(self, message):
        self.APP.received_packet(message)


class WSServer(object):
    def __init__(self, listen, app):
        WSServerTransport.APP = app
        self._listen = listen

    def start(self):
        self._server = WSGIServer(('localhost', 9000), WebSocketWSGIApplication(handler_cls=WSTransport))
        gevent.spawn(self._server.serve_forever())

