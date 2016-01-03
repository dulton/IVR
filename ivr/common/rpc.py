# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
import json
from gevent.queue import Queue
from gevent.lock import RLock
from ivr.common.exception import IVRError
from ivr.common.utils import STRING

import logging
log = logging.getLogger(__name__)

"""
Simple two directional RPC and event notification
over packet/message-based reliable transport (i.e. websocket)

No fancy features as pipeline, bash request etc.

when act as a RPC client, _send_request may raise ErrorResponse, which
means server side exception when handle request; any other Exception raised
by _send_request treated as fatal error, which will close RPC session immediately


"""

"""
request:
{
  req: <method name>
  params: {"key": "value"}
  seq: <sequence number>
}

response:
{
  resp: {"key": "value"}
  seq: <sequence number>
}

error response:
{
  err: {code: <code>, msg: <error message>}
  seq: <sequence number>
}

event:
{
}
"""


class InvalidRPCRequest(IVRError):
    pass


class InvalidRPCMessage(IVRError):
    pass


class ErrorResponse(IVRError):
    pass


class NotOnline(IVRError):
    pass


class JsonEncoder(object):

    @classmethod
    def marshal(self, msg):
        return json.dumps(msg)

    @classmethod
    def unmarshal(self, data):
        return json.loads(data)


class RPCSession(object):
    DEFAULT_ENCODER = JsonEncoder

    def __init__(self, transport=None, encoder=None):
        self._clientSeqNbr = 0
        self._serverSeqNbr = 0
        self._request_mutex = RLock()  # prevent concurrent request
        self._clientQ = Queue(10)
        self._encoder = encoder or self.DEFAULT_ENCODER
        self._transport = transport

    def set_transport(self, transport):
        if self.is_online:
            log.warning("{0} already has transport, closing the old one and replace it".format(self))
            self._transport.force_shutdown()
        self._transport = transport

    def on_received_packet(self, packet):
        # callback from transport
        msg = self._encoder.unmarshal(packet)
        if 'req' in msg:
            self._handle_request(msg)
        elif 'resp' in msg or 'err' in msg:
            self._clientQ.put(msg)
        elif 'event' in msg:
            self._handle_event(msg)

    def _handle_request(self, msg):
        self._serverSeqNbr = msg['seq']
        method = msg['req']
        m = getattr(self, 'rpc_'+method, None)
        if m and callable(m):
            log.info('Received new request {0}: {1}'.format(method, msg.get('params')))
            try:
                if msg.get('params'):
                    result = m(msg['params'])
                else:
                    result = m()
                msg = {'seq': msg['seq'], 'resp': result}
            except Exception as e:
                msg = {'err': {'code': -1, 'msg': STRING(e)}}
            self._transport.send_packet(self._encoder.marshal(msg))
        else:
            raise InvalidRPCRequest("RPC request {0} not implemented".format(method))

    def _handle_event(self, msg):
        method = msg['event']
        m = getattr(self, 'event_'+method, None)
        log.info('Received new event {0}: {1}'.format(method, msg.get('params')))
        if m and callable(m):
            if msg.get('params'):
                m(msg['params'])
            else:
                m()

    def _send_request(self, method, params=None):
        if not self.is_online:
            raise NotOnline("Not on line")
        try:
            with self._request_mutex:
                self._clientSeqNbr += 1
                if params is None:
                    msg = {'req': method,
                           'seq': self._clientSeqNbr}
                else:
                    msg = {'req': method,
                           'params': params,
                           'seq': self._clientSeqNbr}
                self._transport.send_packet(self._encoder.marshal(msg))
                msg = self._clientQ.get(timeout=10)
                if msg['seq'] != self._clientSeqNbr:
                    raise InvalidRPCMessage("Invalid sequence number {0} instead of {1} "
                                            "in response message".format(self.msg['seq'], self._clientSeqNbr))
                if 'err' in msg:
                    raise ErrorResponse(msg['err']['msg'])
                else:
                    return msg.get('resp')
        except ErrorResponse:
            raise
        except Exception:
            self.force_shutdown()
            raise

    def _send_event(self, method, params=None):
        if not self.is_online:
            raise NotOnline("Not on line")
        try:
            if params is None:
                msg = {'event': method}
            else:
                msg = {'event': method,
                       'params': params}
            self._transport.send_packet(self._encoder.marshal(msg))
        except:
            self.force_shutdown()
            raise

    def on_close(self):
        # callback from transport
        self._transport = None

    def force_shutdown(self):
        # called from upper layer
        transport, self._transport = self._transport, None
        if transport:
            transport.force_shutdown()

    @property
    def is_online(self):
        return self._transport is not None and not self._transport.terminated

