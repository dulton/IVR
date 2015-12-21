# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division

from ivr.ivc.rest.common import get_view, post_view, put_view, delete_view
from ivr.ivc.rest.common import get_params_from_request
from ivr.common.schema import Schema, Optional, Default, IntVal


def includeme(config):
    # block device list resource
    # GET:    block device list
    config.add_route('camera_list', '/{project}/cameras')
    config.add_route('camera', '/{project}/cameras/{camera_id}')


get_cameras_list_schema = Schema({Optional('start'): Default(IntVal(min=0), default=0),
                                  Optional('limit'): Default(IntVal(min=0, max=100), default=20)})


@get_view(route_name='camera_list')
def get_camera_list(request):
    req = get_params_from_request(request, get_cameras_list_schema)
    start = req['start']
    limit = req['limit']
    total = request.registry.camera_mngr.get_camera_count()
    resp = {'total': total,
            'start': req['start'],
            'list': []}
    if limit > 0 and start < total:
        camera_list = request.registry.camera_mngr.get_camera_list(request.matchdict['project'],
                                                                   req['start'],
                                                                   req['limit'])
        resp['list'] = camera_list
    return resp


@get_view(route_name='camera')
def get_camera(request):
    return request.registry.camera_mngr.get_camera(request.matchdict['project'],
                                                   request.matchdict['camera_id'])


