# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
import gevent
import datetime
import time
from ivr.common.rpc import RPCSession
from device import DeviceManager
from ivr.common.exception import IVRError
from ivr.common.schema import Schema, STRING, Use

import logging
log = logging.getLogger(__name__)


class DeviceConn(RPCSession):
    def __init__(self, conn_mngr, project_name, device_id, transport, device_ttl):
        super(DeviceConn, self).__init__(transport=transport)
        self._conn_mngr = conn_mngr
        self.project_name = project_name
        self.device_id = device_id
        self._transport = transport
        self._device_ttl = device_ttl
        self._last_keepalive = time.time()
        self._greenlet_chk_ttl = gevent.spawn(self._chk_ttl)

    def on_close(self):
        super(DeviceConn, self).on_close()
        log.info("{0} closed".format(self))
        self._conn_mngr.conn_closed_cbk(self)
        self._greenlet_chk_ttl.kill()

    def force_shutdown(self):
        log.info('Shutdown {0}'.format(self))
        super(DeviceConn, self).force_shutdown()
        self._greenlet_chk_ttl.kill()

    def __str__(self):
        return 'connection with device <{0}> of project <{1}>'.format(self.device_id, self.project_name)

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
        self._last_keepalive = time.time()
        self._conn_mngr.device_keepalive(self.device_id, params)

    def rtmp_publish_stream(self, channel, quality, publish_url, stream_id):
        self._send_request('RTMPPublish', {'channel': channel,
                                           'quality': quality,
                                           'url': publish_url,
                                           'stream_id': stream_id})

    def stop_rtmp_publish(self, channel, stream_id):
        self._send_request('RTMPStopPublish', {'channel': channel,
                                               'stream_id': stream_id})


class DeviceWSConnectionManager(DeviceManager):

    login_params_schema = Schema({'project': Use(STRING),
                                  'login_code': Use(STRING),
                                  'login_passwd': Use(STRING)})

    def __init__(self, device_dao, device_ttl):
        super(DeviceWSConnectionManager, self).__init__(device_dao)
        self._device_ttl = device_ttl
        self._device_connections = {}

    def device_online(self, transport, params):
        params = self.login_params_schema.validate(params)
        project_name = params['project']
        login_code = params['login_code']
        login_passwd = params['login_passwd']
        device = self._dao.get_by_login_code(login_code)
        if not device:
            raise IVRError('Unknown device <{0}> try to login: {1}'.format(login_code, params))
        if device.project_name != project_name:
            raise IVRError('Device <{0}> of project <{1}> attampts to login as project <{2}> device'.format(login_code, device.project_name, project_name))
        if device.login_passwd != login_passwd:
            raise IVRError('Device login failed with wrong password: {0}'.format(params))
        device_conn = DeviceConn(self, project_name, device.uuid, transport, self._device_ttl)
        old_device_conn = self._device_connections.pop(device.uuid, None)
        if old_device_conn:
            log.warning('There is old {0}, disconnect it first'.format(old_device_conn))
            try:
                old_device_conn.force_shutdown()
            except Exception:
                log.exception('failed to force shutdown {0}'.format(old_device_conn))
        self._device_connections[device.uuid] = device_conn
        log.info('{0} online'.format(device))
        device.state = device.STATE_ONLINE
        device.ltime = datetime.datetime.now()
        self._dao.update(device)
        return device_conn

    def device_keepalive(self, device_id, params):
        device_conn = self._device_connections.get(device_id)
        if not device_conn:
            log.error('BUG: device connection not found for keepalive device <{0}>'.format(device_id))
        device = self._dao.get_by_uuid(device_id)
        if not device:
            self._device_connections.pop(device_id, None)
            try:
                device_conn.force_shutdown()
            except Exception:
                log.exception('Failed to force shutdown {0}'.format(device_conn))
            raise IVRError('Unkonw device for {0}'.format(device_conn))
        device.is_online = device.STATE_ONLINE
        device.ltime = datetime.datetime.now()
        self._dao.update(device)
        for channel in params:
            self._camera_mngr.set_camera_state_by_device_channel(device.project_name, device.uuid, channel, params[channel]['is_online'])

    def conn_closed_cbk(self, conn):
        self._device_connections.pop(conn.device_id, None)
        device = self.get_device(conn.project_name, conn.device_id)
        device.is_online = device.STATE_ONLINE
        self.update_device(conn.project_name, device)

    def rtmp_publish_stream(self, project_name, device_id, channel, stream_id, quality, publish_url):
        device_conn = self._device_connections.get(device_id)
        if not device_conn:
            raise IVRError('Device <{0}> of project <{1}> is not online'.format(device_id, project_name))
        device_conn.rtmp_publish_stream(channel, quality, publish_url, stream_id)

    def stop_rtmp_publish(self, project_name, device_id, channel, stream_id):
        device_conn = self._device_connections.get(device_id)
        if not device_conn:
            raise IVRError('Device <{0}> of project <{1}> is not online'.format(device_id, project_name))
        device_conn.stop_rtmp_publish(channel, stream_id)