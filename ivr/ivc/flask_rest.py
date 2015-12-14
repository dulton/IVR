# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify
from flask import request, current_app

from ivr.common.schema import Schema, Optional, Default, IntVal, BoolVal

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


@api.route('/cameras/<camera_id>')
def get_camera(camera_id):
    return jsonify(current_app.camera_mgr.get_camera(camera_id))


get_stream_schema = Schema({Optional('keepalive_required'): Default(BoolVal(), default=False),
                            Optional('create'): Default(BoolVal(), default=True)})


@api.route('/cameras/<camera_id>/live')
def get_live_streams(camera_id):
    return jsonify(current_app.stream_mgr.get_live_streams(camera_id))


@api.route('/cameras/<camera_id>/live/<format>', methods=('post', ))
def request_live_stream(camera_id, format):
    req = get_stream_schema.validate(request.args.to_dict())
    url = current_app.stream_mgr.request_live_stream(camera_id,
                                            format,
                                            keepalive_required=req['keepalive_required'],
                                            create=req['create'])
    print 'response', url
    return jsonify({'url': url})


delete_stream_schema = Schema({Optional('force'): Default(BoolVal(), default=False),})


@api.route('/cameras/<camera_id>/live/<format>', methods=('delete',))
def delete_live_stream(camera_id, format):
    req = delete_stream_schema.validate(request.args.to_dict())
    current_app.stream_mgr.delete_live_stream(camera_id,
                                         format,
                                         req['force'])
    return ''


@api.route('/cameras/<camera_id>/live/<format>/keepalive', methods=('post',))
def keepalive_live_stream(camera_id, format):
    current_app.stream_mgr.keepalive_live_stream(camera_id, format)
    return ''


