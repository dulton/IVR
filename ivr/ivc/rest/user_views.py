# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division

from ivr.ivc.rest.common import get_view, post_view, put_view, delete_view
from ivr.ivc.rest.common import get_params_from_request
from ivr.common.schema import Schema, Optional, Default, IntVal, Use, BoolVal, StrVal, \
    StrRe, DoNotCare, STRING, AutoDel, EnumVal
from pyramid.response import Response


def includeme(config):
    # block device list resource
    # GET:    block device list
    config.add_route('user_list', '/users')
    config.add_route('project_user_list', '/projects/{project_name}/users')
    config.add_route('user', '/users/{username}')
    config.add_route('user_project_list', '/users/{username}/projects')


get_user_list_schema = Schema({
    Optional('filter_key'): StrRe(r"^\S*$"),
    Optional('filter_value'): StrRe(r"^\S*$"),
    Optional('start'): Default(IntVal(min=0), default=0),
    Optional('limit'): Default(IntVal(min=0, max=65535), default=65535),
    DoNotCare(Use(STRING)): object  # for all other key we don't care
})


@get_view(route_name='user_list')
def get_user_list(request):
    params = get_params_from_request(request, get_user_list_schema)
    total, user_list = request.registry.user_mngr.get_user_list_in_pages(
        params.get('filter_key', None),
        params.get('filter_value', ""),
        params['start'],
        params['limit'])
    resp = {'total': total,
            'start': params['start'],
            'list': user_list}
    return resp


@get_view(route_name='project_user_list')
def get_project_user_list(request):
    project_name = request.matchdict['project_name']
    params = get_params_from_request(request, get_user_list_schema)
    total, user_list = request.registry.user_mngr.get_user_list_in_project(
        project_name,
        params.get('filter_key', None),
        params.get('filter_value', ""),
        params['start'],
        params['limit']
    )
    resp = {'total': total,
            'start': params['start'],
            'list': user_list}
    return resp

new_user_schema = Schema({
    "username": StrRe(r"^\w+$"),   # not empty
    "password": StrRe(r"^\w+$"),   # not empty
    Optional("is_privilege"): BoolVal(),
    Optional("title"):  StrRe(r"^\S+$"),
    Optional("desc"): StrRe(r"^\S*$"),
    Optional("long_desc"): StrRe(r"^\S*$"),
    Optional("flags"): Use(int),
    Optional("cellphone"): StrRe(r"^[\d+\-]*$"),
    Optional("email"): StrRe(r"^\w[\w\.-]*@\w[\w\.-]+\.\w+$"),
    AutoDel(STRING): object  # for all other key we delete
})

@post_view(route_name='user_list')
def post_user_list(request):
    params = get_params_from_request(request, new_user_schema)
    user = request.registry.user_mngr.add_user(**params)
    return user


@get_view(route_name='user')
def get_user(request):
    username = request.matchdict['username']
    user = request.registry.user_mngr.get_user(username)
    return user

mod_user_schema = Schema({
    Optional("password"): StrRe(r"^\w+$"),   # not empty
    Optional("title"):  StrRe(r"^\S+$"),
    Optional("desc"): StrRe(r"^\S*$"),
    Optional("long_desc"): StrRe(r"^\S*$"),
    Optional("cellphone"): StrRe(r"^[\d+\-]*$"),
    Optional("email"): StrRe(r"^\w[\w\.-]*@\w[\w\.-]+\.\w+$"),
    DoNotCare(Use(STRING)): object  # for all other key we don't care
})


@put_view(route_name='user')
def put_user(request):
    username = request.matchdict['username']
    params = get_params_from_request(request, mod_user_schema)
    user = request.registry.user_mngr.mod_user(username, **params)
    return user


@delete_view(route_name='user')
def delete_user(request):
    username = request.matchdict['username']
    request.registry.user_mngr.delete_user_by_name(username)
    return Response(status=200)


@get_view(route_name='user_project_list')
def get_user_project_list(request):
    username = request.matchdict['username']
    project_list = request.registry.user_mngr.get_user_projects(username)
    return project_list


project_op_schema = Schema({
    'op': EnumVal(['join', 'leave']),
    'project_name': StrRe(r"^\S+$"),
    DoNotCare(Use(STRING)): object  # for all other key we don't care
})


@post_view(route_name='user_project_list')
def post_user_project_list(request):
    username = request.matchdict['username']
    params = get_params_from_request(request, project_op_schema)
    if params['op'] == 'join':
        request.registry.user_mngr.join_to_project(username, params['project_name'])
    elif params['op'] == 'leave':
        request.registry.user_mngr.leave_from_project(username, params['project_name'])
    return Response(status=200)


