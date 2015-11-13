# -*- coding: utf-8 -*-

from gevent.queue import Queue

"""
{
  req/res/event: <method or event name>
  param/result: {"key": "value"}
  seq: <sequence number>
}
"""


class InvalidRPCRequest(Exception):
    pass


class InvalidRPCMessage(Exception):
    pass


class RPCSession(object):
    def __init__(self, app, transport, encoder):
        self._clientSeqNbr = 0
        self._serverSeqNbr = 0
        self._clientQ = Queue(10)
        self._serverQ = Queue(10)
        self._app = app
        self._encoder = encoder
        self._transport = transport

    def _run(self):
        try:
            while True:
                data = self._transport.recv()
                msg = self._encoder.Unmarshal(data)
                if 'req' in msg:
                    self.handleRequest(msg)
                elif 'res' in msg:
                    self._clientQ.put(msg)
                elif 'event' in msg:
                    self.handleEvent(msg)
        except:
            raise
        finally:
            self._transport.close()

    def handleRequest(self, msg):
        self._serverSeqNbr = msg['seq']
        method = msg['req']
        m = getattr(self._app, 'rpc_'+method, None)
        if m and callable(m):
            if msg.get('param'):
                result = m(msg['param'])
            else:
                result = m()
            msg = {'res': method,
                   'seq': msg['seq']}
            if result:
                msg['result'] = result
            self._transport.send(self._encoder.marshal(msg))
        else:
            raise InvalidRPCRequest("RPC request {0} not implemented".format(method))

    def handleEvent(self, msg):
        method = msg['event']
        m = getattr(self._app, 'event_'+method, None)
        if m and callable(m):
            if msg.get('param'):
                m(msg['param'])
            else:
                m()

    def sendRequest(self, method, param):
        try:
            self._clientSeqNbr += 1
            msg = {'req': method,
                   'param': param,
                   'seq': self._clientSeqNbr}
            self._transport.send(self._encoder.marshal(msg))
            msg = self._clientQ.get(timeout=10)
            if msg['seq'] != self._clientSeqNbr:
                raise InvalidRPCMessage("Invalid sequence number {0} instead of {1} "
                                        "in response message".format(self.msg['seq'], self._clientSeqNbr))
            if msg['res'] != method:
                raise InvalidRPCMessage("Invalid method name {0} in stead of {1} "
                                        "in respone message".format(msg['res'], method))
            return msg.get('result')
        except:
            raise
        finally:
            self.close()

    def sendEvent(self, method, param):
        try:
            msg = {'event': method,
                   'param': param}
            self._transport.send(self._encoder.marshal(msg))
        except:
            raise
        finally:
            self.close()

    def close(self):
        self._transport.close()
