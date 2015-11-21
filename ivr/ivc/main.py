# -*- coding: utf-8 -*-
import gevent.monkey
gevent.monkey.patch_all()

from ivr.common.logger import default_config as default_log_config
from ivr.common.ws import WSServer
from ivr.common.schema import Schema, Use
from ivc import IVC

conf_schema = Schema({
    'listen': Use(str)
})


def main():
    default_log_config()

    config = {
        'listen': '0.0.0.0:5000'
    }

    ivc = IVC()
    server = WSServer(config['listen'], ivc.ivt_online)

    server.server_forever()


if __name__ == '__main__':
    main()
