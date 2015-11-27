# -*- coding: utf-8 -*-
import gevent.monkey
gevent.monkey.patch_all()
import time
import urllib

from ivr.common.logger import default_config as default_log_config
from ivr.common.ws import WSClientTransport
from ivr.common.schema import Schema, Use
from ivr.ivt.ivt import IVT


config_schema = Schema({
    'ivc': Use(str),
    'ivt': Use(str),
})


def main():
    default_log_config()

    config = {
        'ivc': 'ws://127.0.0.1:5000/ivc',
        'id': 'ivt1',
        'cameras': {'c01': {'rtp': 'rtp://x.x.x.x/abc'},
                    'c02': {'rtp': 'rtp://x.x.x.x/xyz'},},
    }

    import logging
    log = logging.getLogger(__name__)

    ivt = IVT(config['id'], config['cameras'])
    WSClientTransport.APP_FACTORY = ivt.ivt_session_factory
    url = config['ivc']+'?'+urllib.urlencode({'id': config['id']})
    while True:
        try:
            client = WSClientTransport(url)
            client.connect()
            client.wait_close()
        except:
            log.exception("Client session closed")
            time.sleep(10)
