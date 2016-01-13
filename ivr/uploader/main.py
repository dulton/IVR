# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
import gevent.monkey
gevent.monkey.patch_all()
import sys
from gevent.wsgi import WSGIServer
from pyramid.response import Response
from ivr.common.logger import default_config as default_log_config
from ivr.common.confparser import parse as parse_conf
from ivr.common.schema import Schema, Use, STRING, Optional


config_schema = Schema({
    'listen': Use(STRING),
    Optional('fs_path'): Use(STRING),
})


def upload_view(request):
    request.registry.upload_service(
        request.matchdict['project_name'],
        request.matchdict['login_code'],
        request.matchdict['channel'],
        request.body_file_raw,
    )
    return Response(status=200)


def main():
    default_log_config(debug=True)
    import logging
    log = logging.getLogger(__name__)

    try:
        if len(sys.argv) == 2:
            config = parse_conf(sys.argv[1])
        else:
            config = parse_conf('uploader.yml')
        config = config_schema.validate(config)

        from pyramid.config import Configurator
        from pyramid.renderers import JSON
        from ivr.common.utils import CustomJSONEncoder
        pyramid_config = Configurator()
        pyramid_config.add_renderer(None, JSON(indent=4, check_circular=True, cls=CustomJSONEncoder))

        if config.get('fs_path'):
            from fs import FSUploadService
            upload_service = FSUploadService(config['fs_path'])
            pyramid_config.registry.upload_service = upload_service
        else:
            raise Exception('No valid upload serivce given')

        pyramid_config.add_route('preview_upload', 'api/ivc/v1/projects/{project_name}/devices/{login_code}/channels/{channel}/upload_preview')
        pyramid_config.add_view(upload_view, route_name='preview_upload', request_method='POST')
        upload_server = WSGIServer(config['listen'], pyramid_config.make_wsgi_app())

        gevent.joinall(map(gevent.spawn, (upload_server.serve_forever, )))
        log.info("Quit")
    except Exception:
        log.exception('Failed to start preview image uploader')