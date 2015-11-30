# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify
from flask import request, current_app

from ivr.common.schema import Schema, Optional, Default, IntVal

import logging
log = logging.getLogger(__name__)

api = Blueprint('stream', __name__)


get_cameras_list_schema = Schema({Optional('start'): Default(IntVal(min=0), default=0),
                                  Optional('limit'): Default(IntVal(min=0, max=100), default=20)})


@api.route('/cameras')
def get_cameras_list():
    req = get_cameras_list_schema.validate(request.args.to_dict())
    start = req['start']
    limit = req['limit']
    total = len(current_app.camera_mgr)
    resp = {'total': total,
            'start': req['start'],
            'list': []}
    if limit > 0 and start < total:
        index = 0
        for camera in current_app.camera_mgr.iter_camera():
            if index >= start:
                if index < start+limit:
                    resp['list'].append(camera)
                else:
                    break
    return jsonify(resp)


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


