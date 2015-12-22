# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
import gevent
import time
from ivr.common.rpc import RPCSession
from manager import DeviceManager
from ivr.common.exception import IVRError


import logging
log = logging.getLogger(__name__)


class DeviceConn(RPCSession):
    def __init__(self, conn_mngr, project_id, device_id, transport, device_ttl):
        self._conn_mngr = conn_mngr
        self._project_id = project_id
        self._device_id = device_id
        self._transport = transport
        self._device_ttl = device_ttl
        self._last_keepalive = time.time()
        self._greenlet_chk_ttl = gevent.spawn(self.chk_ttl)

    def on_close(self):
        super(DeviceConn, self).on_close()
        log.info("{0} disconnected".format(self))
        self._conn_mngr.conn_closed_cbk(self)
        self._greenlet_chk_ttl.kill()

    def force_shutdown(self):
        super(DeviceConn, self).force_shutdown()
        self._greenlet_chk_ttl.kill()

    def __str__(self):
        return 'device "{0}" of project "{1}"'.format(self._id, self._project_id)

    def _chk_ttl(self):
        while True:
            if time.time() > self._last_keepalive + self._device_ttl:
                log.warning('{0} timeout'.format(self))
                self._conn_mngr.conn_closed_cbk(self)
                self.force_shutdown()
            gevent.sleep(30)

    def rpc_echo(self, params):
        return params

    def event_keepalive(self, params):
        # handle keepalive event with states of channels/cameras
        pass

    def rtmp_publish_stream(self, camera_id, quality, publish_url, stream_id):
        self._send_request('RTMPPublish', {'camera_id': camera_id,
                                           'quality': quality,
                                           'url': publish_url,
                                           'stream_id': stream_id})

    def stop_rtmp_publish(self, camera_id, stream_id):
        self._send_request('RTMPStopPublish', {'camera_id': camera_id,
                                               'stream_id': stream_id})


class DeviceWSConnectionManager(DeviceManager):

    def __init__(self, device_dao, device_ttl):
        super(DeviceWSConnectionManager, self).__init__(device_dao)
        self._device_ttl = device_ttl
        self._device_connections = {}

    def device_online(self, transport, params):
        project_id = params.get('project')
        device_id = params.get('uuid')
        if not device_id:
            raise Exception('No device ID is given')
        device = self.get_device(project_id, device_id)
        if not device:
            raise IVRError('Device "{0}" of project "{1}" not recognized'.format(device_id, project_id))
        device_conn = DeviceConn(project_id, device_id, transport)
        self._device_connections[device_id] = device_conn
        device.state = device.STATE_ONLINE
        self.update_device(device)
        return device_conn

    def conn_closed_cbk(self, conn):
        self._device_connections.pop(conn.uuid, None)
        device = self.get_device(conn.project_id, conn.device_id)
        device.state = device.STATE_OFFLINE
        self.update_device(device)
