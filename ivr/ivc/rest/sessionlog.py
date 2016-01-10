# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
import datetime
from pyramid.response import Response
from ivr.ivc.rest.common import get_view, post_view, put_view, delete_view
from ivr.ivc.rest.common import get_params_from_request
from ivr.common.schema import Schema, Optional, Default, BoolVal, EnumVal, Use, STRING, IntVal, StrVal, Datetime


def includeme(config):
    # block device list resource
    # GET:    block device list
    config.add_route('user_session_log_list', '/projects/{project_name}/session_logs')
    config.add_route('user_session_log', '/projects/{project_name}/session_logs/{session_id}')


get_session_log_list_schema = Schema({
    Optional('start_from'): Datetime(),
    Optional('end_to'): Datetime(),
    Optional('limit'): Default(IntVal(min=1, max=512), default=20),
    Optional('last_end_time'): Datetime(),
    Optional('last_session_id'): StrVal(max_len=36),
})


@get_view(route_name='user_session_log_list')
def get_user_session_log_list(request):
    req = get_params_from_request(request, get_session_log_list_schema)
    resp = {'list': []}
    resp['list'] = request.registry.user_session_log_mngr.get_session_log_list(
        request.matchdict['project_name'],
        **req
    )
    return resp


@get_view(route_name='user_session_log')
def get_user_session_log(request):
    return request.registry.user_session_log_mngr.get_session_log(
        request.matchdict['project_name'],
        request.matchdict['session_id']
    )
