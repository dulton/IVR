# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
from pyramid.response import Response
from ivr.common.schema import Schema, Optional, Default, IntVal
from ivr.ivc.rest.common import get_view, post_view, put_view, delete_view
from ivr.ivc.rest.common import get_params_from_request
from ivr.common.schema import Schema, Optional, Default, IntVal, Use, BoolVal, StrVal
from ivr.common.exception import IVRError


def includeme(config):
    config.add_route('project_list', '/projects')
    config.add_route('project', '/projects/{project_name}')


get_project_list_schema = Schema(
    {Optional('start'): Default(IntVal(min=0), default=0),
     Optional('limit'): Default(IntVal(min=0, max=100), default=20)}
)


@get_view(route_name='project_list')
def get_device_list(request):
    req = get_params_from_request(request, get_project_list_schema)
    start = req['start']
    limit = req['limit']
    total = request.registry.project_mngr.get_project_count()
    resp = {'total': total,
            'start': req['start'],
            'list': []}
    if limit > 0 and start < total:
        project_list = request.registry.project_mngr.get_project_list(
            req['start'],
            req['limit']
        )
        resp['list'] = project_list
    return resp


new_device_request_schema = Schema({
    'project_name': StrVal(max_len=64),
    'title': StrVal(max_len=255),
    'max_media_sessions': IntVal(),
    Optional('desc'): StrVal(max_len=255),
    Optional('long_desc'): StrVal(max_len=1024),
})


@post_view(route_name='project_list')
def new_project(request):
    req = get_params_from_request(request, new_device_request_schema)
    request.registry.project_mngr.add_project(project_name=req.pop('project_name'), **req)
    return Response(status=200)


@get_view(route_name='project')
def get_project(request):
    return request.registry.project_mngr.get_project(request.matchdict['project_name'])


@put_view(route_name='project')
def update_project(request):
    pass


@delete_view(route_name='project')
def delete_project(request):
    request.registry.project_mngr.delete_project_by_name(request.matchdict['project_name'])
    return Response(status=200)
