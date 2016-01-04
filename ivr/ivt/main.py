# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
import gevent.monkey
gevent.monkey.patch_all()
import sys
import time
import urllib

from ivr.common.logger import default_config as default_log_config
from ivr.common.ws import WSClientTransport
from ivr.common.schema import Schema, Use, EnumVal, IntVal, ListVal
from ivr.ivt.ivt import IVT
from ivr.common.confparser import parse as parse_conf
from ivr.common.utils import STRING
from ivr.common.datatype import VideoQuality

from streamswitch.port_mngr import SubProcessPort
from streamswitch.ports.rtsp_port import RTSP_PORT_PROGRAM_NAME


config_schema = Schema({
    'ivc': Use(STRING),
    'project': Use(STRING),
    'login_code': Use(STRING),
    'login_passwd': Use(STRING),
    'keepalive_interval': IntVal(min=1, max=1800),
    'cameras': ListVal({
        'channel': IntVal(min=0),
        'type': Use(STRING),
        'streams': ListVal({
            'type': Use(STRING),
            'quality': VideoQuality.schema,
            'url': Use(STRING),
        })
    }),
})


def main():
    default_log_config(debug=True)
    import logging
    log = logging.getLogger(__name__)

    try:
        if len(sys.argv) == 2:
            config = parse_conf(sys.argv[1])
        else:
            config = parse_conf('ivt.yml')
        config = config_schema.validate(config)

        ivt = IVT(config['project'], config['login_code'], config['keepalive_interval'], config['cameras'])

        # start port
        port = SubProcessPort(port_name=config['login_code'], port_type=RTSP_PORT_PROGRAM_NAME)
        port.start()

        # connect to IVC
        WSClientTransport.APP_FACTORY = ivt.ivt_session_factory
        url = config['ivc']+'?'+urllib.urlencode(
            {
                'login_code': config['login_code'],
                'login_passwd': config['login_passwd'],
                'project': config['project']
            }
        )
        while True:
            try:
                client = WSClientTransport(url)
                client.connect()
                client.wait_close()
                time.sleep(10)
            except:
                log.exception("Client session closed")
                time.sleep(10)

    except Exception:
        log.exception('Failed to start IVT')