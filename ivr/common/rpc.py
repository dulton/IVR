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
  result: {"key": "value"}
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


class RPCSession(object):
    DEFAULT_ENCODER = JsonEncoder

    def __init__(self, transport=None, encoder=None):
        self._clientSeqNbr = 0
        self._serverSeqNbr = 0
        self._clientQ = Queue(10)
        self._encoder = encoder or self.DEFAULT_ENCODER
        self._transport = transport

    def set_transport(self, transport):
        if not self.closed:
            log.warning("{0} already has transport, closing the old one and replace it".format(self._app))
            self._transport.force_shutdown()
        self._transport = transport

    def on_received_packet(self, packet):
        # callback from transport
        msg = self._encoder.Unmarshal(packet)
        if 'req' in msg:
            self._handle_request(msg)
        elif 'res' in msg:
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
                    msg['result'] = result
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

    def _send_request(self, method, param):
        try:
            self._clientSeqNbr += 1
            msg = {'req': method,
                   'param': param,
                   'seq': self._clientSeqNbr}
            self._transport.send_packet(self._encoder.marshal(msg))
            msg = self._clientQ.get(timeout=10)
            if msg['seq'] != self._clientSeqNbr:
                raise InvalidRPCMessage("Invalid sequence number {0} instead of {1} "
                                        "in response message".format(self.msg['seq'], self._clientSeqNbr))
            if 'err' in msg:
                raise Exception(msg['err']['msg'])
            else:
                return msg.get('result')
        except:
            raise
        finally:
            self.close()

    def _send_event(self, method, param):
        try:
            msg = {'event': method,
                   'param': param}
            self._transport.send_packet(self._encoder.marshal(msg))
        except:
            raise
        finally:
            self.close()

    def on_close(self):
        # callback from transport
        self._transport = None

    def close_session(self):
        # called from upper layer
        transport, self._transport = self._transport, None
        if transport:
            transport.force_shutdown()

    @property
    def closed(self):
        return self._transport is None or self._transport.terminated


class JsonEncoder(object):

    @classmethod
    def marshal(self, msg):
        return json.dumps(msg)

    @classmethod
    def unmarshal(self, data):
        return json.loads(data)