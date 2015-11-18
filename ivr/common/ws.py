import gevent
from gevent.lock import RLock
from ws4py.server.geventserver import WSGIServer
from ws4py.server.wsgiutils import WebSocketWSGIApplication
from ws4py.websocket import WebSocket
from ws4py.client.geventclient import WebSocketClient


class WSClientTransport(WebSocketClient):
    APP_FACTORY = None

    def __init__(self, url, app):
        # patch socket.sendall to protect it with lock,
        # in order to prevent sending data from multiple greenlets concurrently
        WebSocketClient.__init__(self, url)
        self._app = None
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

    def connect(self):
        super(WSClientTransport, self).connect()
        self._app = self.APP_FACTORY(self)

    def closed(self, code, reason=None):
        self._app.on_close()

    def ponged(self, pong):
        pass

    def received_message(self, message):
        self._app.on_received_packet(message)

    def force_shutdown(self):
        # called by the upper layer, and no callback will be possible when closed
        self._app = None
        self.close()


class WSServerTransport(WebSocket):
    APP_FACTORY = None

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

        # create app
        self.environ
        self._app = self.APP_FACTORY(self, )

    def closed(self, code, reason=None):
        app, self._app = self._app, None
        if app:
            app.on_close()

    def ponged(self, pong):
        pass

    def received_message(self, message):
        self._app.on_received_packet(message)

    def force_shutdown(self):
        # called by the upper layer, and no callback will be possible when closed
        self._app = None
        self.close()


class WSServer(object):
    def __init__(self, listen, app_factory):
        WSServerTransport.APP_FACTORY = app_factory
        self._listen = listen

    def start(self):
        self._server = WSGIServer(self._listen, WebSocketWSGIApplication(handler_cls=WSServerTransport))
        gevent.spawn(self._server.serve_forever())

