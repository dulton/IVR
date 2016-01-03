# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
import urlparse

from gevent.lock import RLock
from gevent.event import Event
from ws4py.server.geventserver import WSGIServer
from ws4py.server.wsgiutils import WebSocketWSGIApplication
from ws4py.websocket import WebSocket
from ws4py.client.geventclient import WebSocketClient
from ivr.common.utils import STRING

import logging
log = logging.getLogger(__name__)


class WSClientTransport(WebSocketClient):
    APP_FACTORY = None

    def __init__(self, url):
        self._close_event = Event()
        # patch socket.sendall to protect it with lock,
        # in order to prevent sending data from multiple greenlets concurrently
        WebSocketClient.__init__(self, url)
        self._app = None
        self._lock = RLock()
        _sendall = self.sock.sendall

        def sendall(data):
            self._lock.acquire()
            try:
                _sendall(data)
            except:
                raise
            finally:
                self._lock.release()
        self.sock.sendall = sendall

    def connect(self):
        super(WSClientTransport, self).connect()
        self._app = self.APP_FACTORY(self)
        log.info("Connected to websocket server {0}".format(self.url))

    def closed(self, code, reason=None):
        if self._app:
            self._app.on_close()
        self._close_event.set()

    def ponged(self, pong):
        pass

    def received_message(self, message):
        log.debug("Received message {0}".format(message))
        self._app.on_received_packet(STRING(message))

    def send_packet(self, data):
        log.debug("Sending message {0}".format(data))
        self.send(data)

    def force_shutdown(self):
        # called by the upper layer, and no callback will be possible when closed
        self._app = None
        self.close()
        self._close_event.set()

    def wait_close(self):
        self._close_event.wait()


class WSServerTransport(WebSocket):
    APP_FACTORY = None

    def __init__(self, *args, **kwargs):
        super(WSServerTransport, self).__init__(*args, **kwargs)
        self._app = None

    def opened(self):
        # patch socket.sendall to protect it with lock,
        # in order to prevent sending data from multiple greenlets concurrently
        self._lock = RLock()
        _sendall = self.sock.sendall

        def sendall(data):
            self._lock.acquire()
            try:
                _sendall(data)
            except:
                raise
            finally:
                self._lock.release()
        self.sock.sendall = sendall

        # create app
        if not self.environ.get('QUERY_STRING'):
            query = {}
        else:
            query = urlparse.parse_qs(self.environ['QUERY_STRING'])
        for key, value in query.iteritems():
            query[key] = value[0]
        self._app = self.APP_FACTORY(self, query)

    def closed(self, code, reason=None):
        app, self._app = self._app, None
        if app:
            app.on_close()

    def ponged(self, pong):
        pass

    def received_message(self, message):
        log.debug("Received message {0}".format(message))
        self._app.on_received_packet(STRING(message))

    def send_packet(self, data):
        log.debug("Sending message {0}".format(data))
        self.send(data)

    def force_shutdown(self):
        # called by the upper layer, and no callback will be possible when closed
        log.info("shutdown")
        self._app = None
        self.close()


class WSServer(object):
    def __init__(self, listen, app_factory):
        WSServerTransport.APP_FACTORY = app_factory
        self._listen = listen

    def server_forever(self):
        self._server = WSGIServer(self._listen, WebSocketWSGIApplication(handler_cls=WSServerTransport))
        log.info("Starting server on {0}".format(self._listen))
        self._server.serve_forever()

