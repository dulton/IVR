# -*- coding: utf-8 -*-
import json

from gevent.queue import Queue

import logging
log = logging.getLogger(__name__)

"""
request:
{
  req: <method name>
  param: {"key": "value"}
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


class InvalidRPCRequest(Exception):
    pass


class InvalidRPCMessage(Exception):
    pass


class ErrorResponse(Exception):
    pass


class NotOnline(Exception):
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
        self._clientQ = Queue(10)
        self._encoder = encoder or self.DEFAULT_ENCODER
        self._transport = transport

    def set_transport(self, transport):
        if not self.is_online:
            log.warning("{0} already has transport, closing the old one and replace it".format(self._app))
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
            try:
                if msg.get('param'):
                    result = m(msg['param'])
                else:
                    result = m()
                msg = {'seq': msg['seq']}
                if result:
                    msg['resp'] = result
            except Exception as e:
                msg = {'err': {'code': -1, 'msg': str(e)}}
            self._transport.send_packet(self._encoder.marshal(msg))
        else:
            raise InvalidRPCRequest("RPC request {0} not implemented".format(method))

    def _handle_event(self, msg):
        method = msg['event']
        m = getattr(self, 'event_'+method, None)
        if m and callable(m):
            if msg.get('param'):
                m(msg['param'])
            else:
                m()

    def _send_request(self, method, param=None):
        if not self.is_online:
            raise NotOnline("Not on line")
        try:
            self._clientSeqNbr += 1
            if param is None:
                msg = {'req': method,
                       'seq': self._clientSeqNbr}
            else:
                msg = {'req': method,
                       'param': param,
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

    def _send_event(self, method, param=None):
        if not self.is_online:
            raise NotOnline("Not on line")
        try:
            if param is None:
                msg = {'event': method}
            else:
                msg = {'event': method,
                       'param': param}
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

