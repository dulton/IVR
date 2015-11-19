# -*- coding: utf-8 -*-
import gevent.monkey
gevent.monkey.patch_all()
import time

from ivr.common.logger import default_config
from ivr.common.ws import WSClientTransport
from ivr.ivt.ivt import IVT


def main():
    default_config()

    config = {
        'ivc': 'ws://127.0.0.1:5000/ws'
    }

    import logging
    log = logging.getLogger(__name__)

    ivt = IVT()
    WSClientTransport.APP_FACTORY = ivt.ivt_session_factory
    while True:
        try:
            client = WSClientTransport(config['ivc'])
            client.connect()
            client.wait_close()
        except:
            log.exception("Client session closed")
            time.sleep(10)
