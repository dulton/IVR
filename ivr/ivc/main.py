# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division

import gevent.monkey

gevent.monkey.patch_all()

from gevent.wsgi import WSGIServer

import sys
from ivr.common.logger import default_config as default_log_config
from ivr.common.ws import WSServer
from ivr.common.schema import Schema, Use, IntVal, Default, Optional, BoolVal
from ivr.common.confparser import parse as parse_conf
from ivr.ivc.manager.camera import CameraManager
from ivr.ivc.manager.device_ws import DeviceWSConnectionManager
from ivr.ivc.manager.session import UserSessionManager
from ivr.ivc.manager.stream import StreamManager
from ivr.ivc.manager.project import ProjectManager

config_schema = Schema({
    'rest_listen': Use(str),
    'ws_listen': Use(str),
    'rtmp_publish_url_prefix': Use(str),
    'rtmp_url_prefix': Use(str),
    'hls_url_prefix': Use(str),
    'stream_ttl': IntVal(min=10, max=1800),
    'user_session_ttl': IntVal(min=10, max=1800),
    'device_ttl': IntVal(min=10, max=1800),
    Optional('sqlalchemy'): {
        'url': Use(str)
    },
    Optional('debug'): Default(BoolVal(), default=False),
})


def main():
    default_log_config(debug=True)
    import logging
    log = logging.getLogger(__name__)

    try:
        if (sys.argv) == 2:
            config = parse_conf(sys.argv[1])
        else:
            config = parse_conf('ivc.yml')
        config = config_schema.validate(config)

        # prepare data backend
        if config.get('sqlalchemy'):
            from sqlalchemy import engine_from_config
            from ivr.ivc.daos.sa_dao_context_mngr import AlchemyDaoContextMngr
            from ivr.ivc.daos.sa_camera_dao import SACameraDao
            from ivr.ivc.daos.sa_device_dao import SADeviceDao
            from ivr.ivc.daos.sa_project_dao import SAProjectDao
            engine = engine_from_config(config['sqlalchemy'], prefix='')
            dao_context_mngr = AlchemyDaoContextMngr(engine)
            project_dao = SAProjectDao(dao_context_mngr)
            camera_dao = SACameraDao(dao_context_mngr)
            device_dao = SADeviceDao(dao_context_mngr)
            from ivr.ivc.dummy_daos import UserSessionDAO, StreamDAO
            stream_dao = StreamDAO()
            user_session_dao = UserSessionDAO()
        else:
            from ivr.ivc.dummy_daos import CameraDAO, UserSessionDAO, StreamDAO, DeviceDAO
            camera_dao = CameraDAO()
            stream_dao = StreamDAO()
            user_session_dao = UserSessionDAO()
            device_dao = DeviceDAO()

        project_mngr = ProjectManager(project_dao)
        if not config['ws_listen']:
            from ivr.ivc.manager.device import DummyDeviceManager
            device_mngr = DummyDeviceManager(device_dao)
        else:
            device_mngr = DeviceWSConnectionManager(device_dao, config['device_ttl'])
        camera_mngr = CameraManager(camera_dao, device_mngr)
        stream_mngr = StreamManager(stream_dao,
                                    camera_mngr,
                                    config['rtmp_publish_url_prefix'],
                                    config['rtmp_url_prefix'],
                                    config['hls_url_prefix'],
                                    stream_ttl=config['stream_ttl'])
        user_session_mngr = UserSessionManager(user_session_dao,
                                               stream_mngr,
                                               config['user_session_ttl'])

        # prepare REST API
        from pyramid.config import Configurator
        from pyramid.renderers import JSON
        from ivr.common.utils import CustomJSONEncoder
        pyramid_config = Configurator()
        pyramid_config.add_renderer(None, JSON(indent=4, check_circular=True, cls=CustomJSONEncoder))
        pyramid_config.include('ivr.ivc.rest', route_prefix='api/ivc/v1')
        pyramid_config.registry.project_mngr = project_mngr
        pyramid_config.registry.device_mngr = device_mngr
        pyramid_config.registry.camera_mngr = camera_mngr
        pyramid_config.registry.stream_mngr = stream_mngr
        pyramid_config.registry.user_session_mngr = user_session_mngr
        if config.get('debug'):
            pyramid_config.add_settings({'debugtoolbar.hosts': ['0.0.0.0/0', '::1'],
                                 'debugtoolbar.enabled': True,
                                 'pyramid.debug_authorization': False,})
            pyramid_config.include('pyramid_debugtoolbar')
            pyramid_config.include('pyramid_chameleon')
        rest_server = WSGIServer(config['rest_listen'], pyramid_config.make_wsgi_app())

        # start server and wait
        if config['ws_listen']:
            ws_server = WSServer(config['ws_listen'], device_mngr.device_online)
            gevent.joinall(map(gevent.spawn, (ws_server.server_forever, rest_server.serve_forever)))
        else:
            gevent.joinall(map(gevent.spawn, (rest_server.serve_forever, )))
        log.info("Quit")
    except Exception:
        log.exception("Failed to start IVC")

if __name__ == '__main__':
    main()
