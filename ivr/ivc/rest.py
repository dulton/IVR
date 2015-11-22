# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify
from flask import request, current_app

import logging
log = logging.getLogger(__name__)

api = Blueprint('stream', __name__)


@api.route('/cameras/<camera_id>/streams/<stream_id>')
def get_stream(camera_id, stream_id):
    return jsonify({'url': 'hls/abc.m3u8'})


@api.route('/cameras/<camera_id>/streams/<stream_id>', methods=('delete',))
def delete_stream(camera_id, stream_id):
    return ''


@api.route('/cameras/<camera_id>/streams/<stream_id>/keepalive')
def keepalive_stream(camera_id, stream_id):
    return ''


