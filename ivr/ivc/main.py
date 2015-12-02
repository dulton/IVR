# -*- coding: utf-8 -*-
import gevent.monkey
gevent.monkey.patch_all()

from gevent.wsgi import WSGIServer
from flask import Flask, request

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
        config = {
            'rest_listen': '0.0.0.0:5001',
            'ws_listen': '0.0.0.0:5000',
            'rtmp_publish_url_prefix': 'rtmp://121.41.72.231/live/',
            'stream_ttl': 20,
        }

        camera_mgr = CameraManager()
        stream_mgr = StreamManager(camera_mgr,
                                   config['rtmp_publish_url_prefix'],
                                   stream_ttl=config['stream_ttl'])
        ws_server = WSServer(config['ws_listen'], camera_mgr.ivt_online)

        def handle_ivr_error(error):
            return str(error), error.http_status_code

        rest_app = Flask(__name__)
        from ivr.ivc.rest import api as ivc_rest
        rest_app.register_blueprint(ivc_rest, url_prefix='/api/ivc/v1')
        rest_app.stream_mgr = stream_mgr
        rest_app.camera_mgr = camera_mgr
        rest_app.register_error_handler(IVRError, handle_ivr_error)

        @rest_app.after_request
        def add_cors_header(response):
            if request.method == 'OPTIONS':
                response.headers['Access-Control-Allow-Methods'] = response.headers['Allow']
                response.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept'
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response

        rest_server = WSGIServer(config['rest_listen'], rest_app)

        gevent.joinall(map(gevent.spawn, (ws_server.server_forever, rest_server.serve_forever)))
        log.info("Quit")
    except Exception:
        log.exception("Failed to start IVC")

if __name__ == '__main__':
    main()
