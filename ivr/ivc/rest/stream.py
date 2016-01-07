# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
from pyramid.response import Response
from ivr.ivc.rest.common import get_view, post_view, put_view, delete_view
from ivr.ivc.rest.common import get_params_from_request
from ivr.common.datatype import VideoQuality
from ivr.common.schema import Schema, BoolVal, Default, Optional, IntVal


def includeme(config):
    config.add_route('stream_list', '/projects/{project_name}/cameras/{camera_id}/streams')
    config.add_route('stream', '/projects/{project_name}/cameras/{camera_id}/streams/{stream_id}')


get_cameras_list_schema = Schema({Optional('start'): Default(IntVal(min=0), default=0),
                                  Optional('limit'): Default(IntVal(min=0, max=100), default=20)})


@get_view(route_name='stream_list')
def get_stream_list(request):
    req = get_params_from_request(request, get_cameras_list_schema)
    start = req['start']
    limit = req['limit']
    total = request.registry.stream_mngr.get_stream_count(request.matchdict['project_name'], request.matchdict['camera_id'])
    resp = {'total': total,
            'start': req['start'],
            'list': []}
    if limit > 0 and start < total:
        stream_list = request.registry.stream_mngr.get_stream_list(request.matchdict['project_name'],
                                                                   request.matchdict['camera_id'],
                                                                   req['start'],
                                                                   req['limit'])
        resp['list'] = stream_list
    return resp

start_stream_schema = Schema({
    'quality': VideoQuality.schema,
    Optional('autodelete'): Default(BoolVal(), default=False)
})


@post_view(route_name='stream_list')
def start_stream(request):
    req = get_params_from_request(request, start_stream_schema)
    stream = request.register.stream_mngr.request_stream(
        request.matchdict['project_name'],
        request.matchdict['camera_id'],
        stream_format='rtmp',
        stream_quality=req['quality'],
        auto_delete=req['autodelete'],
        create=True,
    )
    return {'stream_id': stream.id}



@get_view(route_name='stream')
def get_stream_info(request):
    return request.registry.stream_mngr.get_stream(
        request.matchdict['project_name'],
        request.matchdict['camera_id'],
        request.matchdict['stream_id']
    )


@delete_view(route_name='stream')
def stop_stream(request):
    return request.registry.stream_mngr.stop_stream(
        request.matchdict['project_name'],
        request.matchdict['camera_id'],
        request.matchdict['stream_id']
    )
    return Response(status=200)