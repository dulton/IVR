# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
from pyramid.response import Response
from ivr.ivc.rest.common import get_view, post_view, put_view, delete_view
from ivr.ivc.rest.common import get_params_from_request
from ivr.common.schema import Schema, Optional, Default, IntVal, Use, BoolVal, StrVal


def includeme(config):
    # block device list resource
    # GET:    block device list
    config.add_route('camera_list', '/projects/{project_name}/cameras')
    config.add_route('camera', '/projects/{project_name}/cameras/{camera_id}')


get_cameras_list_schema = Schema({Optional('start'): Default(IntVal(min=0), default=0),
                                  Optional('limit'): Default(IntVal(min=0, max=100), default=20)})


@get_view(route_name='camera_list')
def get_camera_list(request):
    req = get_params_from_request(request, get_cameras_list_schema)
    start = req['start']
    limit = req['limit']
    total = request.registry.camera_mngr.get_camera_count(request.matchdict['project_name'])
    resp = {'total': total,
            'start': req['start'],
            'list': []}
    if limit > 0 and start < total:
        camera_list = request.registry.camera_mngr.get_camera_list(request.matchdict['project_name'],
                                                                   req['start'],
                                                                   req['limit'])
        resp['list'] = camera_list
    return resp


new_camera_request_schema = Schema({
    'name': StrVal(max_len=255),
    Optional('desc'): StrVal(max_len=255),
    Optional('long_desc'): StrVal(max_len=1024),
    'device_uuid': Use(unicode),
    'channel_index': IntVal(min=0),
    'flags': IntVal(),
    Optional('longitude'): Use(float),
    Optional('latitude'): Use(float),
    Optional('altitude'): Use(float),
})


@post_view(route_name='camera_list')
def new_camera(request):
    req = get_params_from_request(request, new_camera_request_schema)
    camera_id = request.registry.camera_mngr.add_camera(project_name=request.matchdict['project_name'], **req)
    return {'uuid': camera_id}


@get_view(route_name='camera')
def get_camera(request):
    return request.registry.camera_mngr.get_camera(request.matchdict['project_name'],
                                                   request.matchdict['camera_id'])


@put_view(route_name='camera')
def update_camera(request):
    pass


@delete_view(route_name='camera')
def delete_camera(request):
    request.registry.camera_mngr.delete_camera_by_id(request.matchdict['project_name'], request.matchdict['camera_id'])
    return Response(status=200)


