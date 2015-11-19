# -*- coding: utf-8 -*-
import gevent.monkey
gevent.monkey.patch_all()

from ivr.common.logger import default_config
from ivr.common.ws import WSServer
from ivc import IVC


def main():
    default_config()

    config = {
        'listen': ('localhost', 5000)
    }

    ivc = IVC()
    server = WSServer(config['listen'], ivc.ivt_online)

    server.server_forever()


if __name__ == '__main__':
    main()
