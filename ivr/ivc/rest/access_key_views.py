# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division

from ivr.ivc.rest.common import get_view, post_view, put_view, delete_view
from ivr.ivc.rest.common import get_params_from_request
from ivr.common.schema import Schema, Optional, Default, IntVal, Use, BoolVal, StrVal, \
    StrRe, DoNotCare, STRING, AutoDel, EnumVal
from pyramid.response import Response
from ..manager.access_key import AccessKey
from ...common.exception import IVRError

def includeme(config):
    # block device list resource
    # GET:    block device list
    config.add_route('access_key_list', '/access_keys')
    config.add_route('user_access_key_list', '/users/{username}/access_keys')
    config.add_route('access_key', '/access_keys/{key_id}')
    config.add_route('access_key_secret', '/access_keys/{key_id}/secret')


get_access_key_list_schema = Schema({
    Optional('username'): StrRe(r"^\w*$"),
    Optional('key_type'): IntVal(values=[AccessKey.KEY_TYPE_NORMAL,
                                         AccessKey.KEY_TYPE_PRIVILEGE]),
    Optional('start'): Default(IntVal(min=0), default=0),
    Optional('limit'): Default(IntVal(min=0, max=65535), default=65535),
    DoNotCare(Use(STRING)): object  # for all other key we don't care
})


@get_view(route_name='access_key_list')
def get_access_key_list(request):
    params = get_params_from_request(request, get_access_key_list_schema)
    total, access_key_list = request.registry.access_key_mngr.get_key_list_in_pages(
        username=params.get('username', None),
        key_type=params.get('key_type', None),
        start_index=params['start'],
        max_number=params['limit'])
    resp = {'total': total,
            'start': params['start'],
            'list': access_key_list}
    return resp


@get_view(route_name='user_access_key_list')
def get_user_access_key_list(request):
    username = request.matchdict['username']
    params = get_params_from_request(request, get_access_key_list_schema)
    total, access_key_list = request.registry.access_key_mngr.get_key_list_in_pages(
        username=username,
        start_index=params['start'],
        max_number=params['limit']
    )
    resp = {'total': total,
            'start': params['start'],
            'list': access_key_list}
    return resp

new_access_key_schema = Schema({
    Optional('username'): StrRe(r"^\w+$"),
    Optional("enabled"): BoolVal(),
    Optional('key_type'): IntVal(values=[AccessKey.KEY_TYPE_NORMAL,
                                         AccessKey.KEY_TYPE_PRIVILEGE]),
    Optional("desc"): StrRe(r"^\S*$"),
    AutoDel(STRING): object  # for all other key we delete
})


@post_view(route_name='access_key_list')
def post_access_key_list(request):
    params = get_params_from_request(request, new_access_key_schema)
    if 'username' not in params:
        raise IVRError("username absent", 400)
    access_key = request.registry.access_key_mngr.new_access_key(**params)
    return access_key


@post_view(route_name='user_access_key_list')
def post_user_access_key_list(request):
    username = request.matchdict['username']
    params = get_params_from_request(request, new_access_key_schema)
    params['username'] = username
    access_key = request.registry.access_key_mngr.new_access_key(**params)
    return access_key


@get_view(route_name='access_key')
def get_access_key(request):
    key_id = request.matchdict['key_id']
    access_key = request.registry.access_key_mngr.get_access_key(key_id)
    return access_key


@get_view(route_name='access_key_secret')
def get_access_key_secret(request):
    key_id = request.matchdict['key_id']
    secret = request.registry.access_key_mngr.get_key_secret(key_id)
    return {"secret": secret}

mod_access_key_schema = Schema({
    Optional("enabled"): BoolVal(),
    Optional("desc"): StrRe(r"^\S*$"),
    DoNotCare(Use(STRING)): object  # for all other key we don't care
})


@put_view(route_name='access_key')
def put_access_key(request):
    key_id = request.matchdict['key_id']
    params = get_params_from_request(request, mod_access_key_schema)
    user = request.registry.access_key_mngr.mod_access_key(key_id, **params)
    return user


@delete_view(route_name='access_key')
def delete_access_key(request):
    key_id = request.matchdict['key_id']
    request.registry.access_key_mngr.del_access_key(key_id)
    return Response(status=200)

