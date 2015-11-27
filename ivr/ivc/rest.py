# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify
from flask import request, current_app

import logging
log = logging.getLogger(__name__)

api = Blueprint('stream', __name__)


@api.route('/cameras/<camera_id>/streams/<format>')
def get_stream(camera_id, format):
    url = current_app.stream_mgr.get_stream(camera_id,
                                            format,
                                            keepalive_required=request.args.get('keepalive_required', False),
                                            create=request.args.get('create', True))
    return jsonify({'url': url})


@api.route('/cameras/<camera_id>/streams/<format>', methods=('delete',))
def delete_stream(camera_id, format):
    current_app.stream_mgr.delete_stream(camera_id,
                                         format,
                                         request.args.get('force', False))
    return ''


@api.route('/cameras/<camera_id>/streams/<format>/keepalive', methods=('post',))
def keepalive_stream(camera_id, format):
    current_app.stream_mgr.keepalive_stream(camera_id, format)
    return ''


