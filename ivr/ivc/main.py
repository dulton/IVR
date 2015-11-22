# -*- coding: utf-8 -*-
import gevent.monkey
gevent.monkey.patch_all()

from gevent.wsgi import WSGIServer
from flask import Flask

from ivr.common.logger import default_config as default_log_config
from ivr.common.ws import WSServer
from ivr.common.schema import Schema, Use
from ivc import IVC

conf_schema = Schema({
    'rest_listen': Use(str),
    'ws_listen': Use(str),
})


def main():
    default_log_config()

    config = {
        'rest_listen': '0.0.0.0:5001',
        'ws_listen': '0.0.0.0:5000',
    }

    ivc = IVC()
    ws_server = WSServer(config['ws_listen'], ivc.ivt_online)

    rest_app = Flask(__name__)
    from ivr.ivc.rest import api as ivc_rest
    rest_app.register_blueprint(ivc_rest)
    rest_app.ivc = ivc
    rest_server = WSGIServer(config['rest_listen'], rest_app)

    gevent.joinall(map(gevent.spawn, (ws_server.server_forever, rest_server.serve_forever)))


if __name__ == '__main__':
    main()
