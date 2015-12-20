# -*- coding: utf-8 -*-
import gevent.monkey
gevent.monkey.patch_all()

from gevent.wsgi import WSGIServer

from ivr.common.logger import default_config as default_log_config
from ivr.common.ws import WSServer
from ivr.common.schema import Schema, Use
from ivr.common.exception import IVRError
from ivc import CameraManager, StreamManager

conf_schema = Schema({
    'rest_listen': Use(str),
    'ws_listen': Use(str),
})


def main():
    default_log_config(debug=True)
    import logging
    log = logging.getLogger(__name__)

    try:
        conf = {
            'rest_listen': '0.0.0.0:5001',
            'ws_listen': '0.0.0.0:5000',
            'rtmp_publish_url_prefix': 'rtmp://121.41.72.231/live/',
            'stream_ttl': 20,
            'debug': True,
        }

        camera_mngr = CameraManager()
        stream_mngr = StreamManager(camera_mngr,
                                   conf['rtmp_publish_url_prefix'],
                                   stream_ttl=conf['stream_ttl'])
        ws_server = WSServer(conf['ws_listen'], camera_mngr.ivt_online)

        from pyramid.config import Configurator
        from pyramid.renderers import JSON
        from ivr.common.rest import CustomJSONEncoder
        config = Configurator()
        config.add_renderer(None, JSON(indent=4, check_circular=True, cls=CustomJSONEncoder))
        config.include('ivr.ivc.rest', route_prefix='api/ivc/v1')
        config.registry.camera_mngr = camera_mngr
        config.registry.stream_mngr = stream_mngr
        if conf.get('debug'):
            config.add_settings({'debugtoolbar.hosts': ['0.0.0.0/0', '::1'],
                                 'debugtoolbar.enabled': True,
                                 'pyramid.debug_authorization': False,})
            config.include('pyramid_debugtoolbar')
            config.include('pyramid_chameleon')
        rest_server = WSGIServer(conf['rest_listen'], config.make_wsgi_app())

        gevent.joinall(map(gevent.spawn, (ws_server.server_forever, rest_server.serve_forever)))
        log.info("Quit")
    except Exception:
        log.exception("Failed to start IVC")

if __name__ == '__main__':
    main()
