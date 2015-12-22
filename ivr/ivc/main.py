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
from ivr.ivc.manager.session import UserSessionManager
from ivr.ivc.manager.stream import StreamManager

config_schema = Schema({
    'rest_listen': Use(str),
    'ws_listen': Use(str),
    'rtmp_publish_url_prefix': Use(str),
    'stream_ttl': IntVal(min=10, max=1800),
    'user_session_ttl': IntVal(min=10, max=1800),
    Default('debug'): Optional(BoolVal(), default=False),
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
        if not config.get('mysql'):
            from ivr.ivc.backend.dummy_mem import CameraDAO, UserSessionDAO, StreamDAO
            camera_dao = CameraDAO()
            stream_dao = StreamDAO()
            user_session_dao = UserSessionDAO()
        else:
            pass

        camera_mngr = CameraManager(camera_dao)
        stream_mngr = StreamManager(stream_dao,
                                    camera_mngr,
                                    config['rtmp_publish_url_prefix'],
                                    stream_ttl=config['stream_ttl'])
        user_session_mngr = UserSessionManager(user_session_dao,
                                               stream_mngr,
                                               config['user_session_ttl'])


        # prepare websocket server
        ws_server = WSServer(config['ws_listen'], camera_mngr.ivt_online)

        # prepare REST API
        from pyramid.config import Configurator
        from pyramid.renderers import JSON
        from ivr.common.rest import CustomJSONEncoder
        config = Configurator()
        config.add_renderer(None, JSON(indent=4, check_circular=True, cls=CustomJSONEncoder))
        config.include('ivr.ivc.rest', route_prefix='api/ivc/v1')
        config.registry.camera_mngr = camera_mngr
        config.registry.stream_mngr = stream_mngr
        if config.get('debug'):
            config.add_settings({'debugtoolbar.hosts': ['0.0.0.0/0', '::1'],
                                 'debugtoolbar.enabled': True,
                                 'pyramid.debug_authorization': False,})
            config.include('pyramid_debugtoolbar')
            config.include('pyramid_chameleon')
        rest_server = WSGIServer(config['rest_listen'], config.make_wsgi_app())

        # start server and wait
        gevent.joinall(map(gevent.spawn, (ws_server.server_forever, rest_server.serve_forever)))
        log.info("Quit")
    except Exception:
        log.exception("Failed to start IVC")

if __name__ == '__main__':
    main()
