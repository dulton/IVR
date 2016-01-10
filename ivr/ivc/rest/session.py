# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
from pyramid.response import Response
from ivr.ivc.rest.common import get_view, post_view, put_view, delete_view
from ivr.ivc.rest.common import get_params_from_request
from ivr.common.schema import Schema, Optional, Default, BoolVal, EnumVal, Use, STRING, IntVal


def includeme(config):
    # block device list resource
    # GET:    block device list
    config.add_route('user_session_list', '/projects/{project_name}/cameras/{camera_id}/sessions')
    config.add_route('user_session', '/projects/{project_name}/cameras/{camera_id}/sessions/{session_id}')


get_running_session_list_schema = Schema({
    Optional('start'): Default(IntVal(min=0), default=0),
    Optional('limit'): Default(IntVal(min=0, max=100), default=20)
})


@get_view(route_name='user_session_list')
def get_running_user_session_list(request):
    req = get_params_from_request(request, get_running_session_list_schema)
    start = req['start']
    limit = req['limit']
    total = request.registry.user_session_mngr.get_running_session_count(
        request.matchdict['project_name'],
        camera_id=request.matchdict['camera_id']
    )
    resp = {'total': total,
            'start': req['start'],
            'list': []}
    if limit > 0 and start < total:
        session_list = request.registry.user_session_mngr.get_running_session_list(
            request.matchdict['project_name'],
            camera_id=request.matchdict['camera_id'],
            start=req['start'],
            limit=req['limit']
        )
        resp['list'] = session_list
    return resp


get_stream_schema = Schema({'format': EnumVal(['hls', 'rtmp']),
                            Optional('quality'): Default(EnumVal(['ld', 'sd', 'hd']), default='ld'),
                            Optional('create'): Default(BoolVal(), default=True),
                            Optional('user'): Default(Use(STRING), default='')})


@post_view(route_name='user_session_list')
def request_user_session(request):
    req = get_params_from_request(request, get_stream_schema)
    url, session_id = request.registry.user_session_mngr.request_session(
        request.matchdict['project_name'],
        request.matchdict['camera_id'],
        stream_format=req['format'],
        stream_quality=req['quality'],
        create=req['create'],
        ip=request.client_addr or '',
        user_agent=request.user_agent,
        username='',
        subuser=req['user']
    )
    return {'url': url, 'session_id': session_id}


@delete_view(route_name='user_session')
def delete_user_session(request):
    request.registry.user_session_mngr.stop_session(
        request.matchdict['project_name'],
        request.matchdict['camera_id'],
        request.matchdict['session_id']
    )
    return Response(status=200)


@post_view(route_name='user_session')
def keepalive_user_session(request):
    request.registry.user_session_mngr.keepalive_session(
        request.matchdict['project_name'],
        request.matchdict['camera_id'],
        request.matchdict['session_id']
    )
    return Response(status=200)


