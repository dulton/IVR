# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
from ivr.common.schema import Schema, Optional, Default, IntVal
from ivr.ivc.rest.common import get_view, post_view, put_view, delete_view
from ivr.ivc.rest.common import get_params_from_request
from ivr.common.schema import Schema, Optional, Default, IntVal, Use, BoolVal, StrVal


def includeme(config):
    # block device list resource
    # GET:    block device list
    config.add_route('device_list', '/projects/{project_name}/devices')
    config.add_route('device', '/projects/{project_name}/devices/{device_id}')


get_devices_list_schema = Schema(
    {Optional('start'): Default(IntVal(min=0), default=0),
     Optional('limit'): Default(IntVal(min=0, max=100), default=20)}
)


@get_view(route_name='device_list')
def get_device_list(request):
    req = get_params_from_request(request, get_devices_list_schema)
    start = req['start']
    limit = req['limit']
    total = request.registry.device_mngr.get_device_count(request.matchdict['project_name'])
    resp = {'total': total,
            'start': req['start'],
            'list': []}
    if limit > 0 and start < total:
        device_list = request.registry.device_mngr.get_device_list(
            request.matchdict['project_name'],
            req['start'],
            req['limit']
        )
        resp['list'] = device_list
    return resp


new_device_request_schema = Schema({
    'name': StrVal(max_len=255),
    'type': StrVal(max_len=32),
    'flags': IntVal(),
    Optional('login_code'): StrVal(max_len=64),
    'login_passwd': StrVal(max_len=64),
    Optional('firmware_model'): StrVal(max_len=255),
    Optional('hardware_model'): StrVal(max_len=255),
    # Optional('media_channel_num'): IntVal(),
    Optional('desc'): StrVal(max_len=255),
    Optional('long_desc'): StrVal(max_len=1024),
    Optional('longitude'): Use(float),
    Optional('latitude'): Use(float),
    Optional('altitude'): Use(float),
})


@post_view(route_name='device_list')
def new_device(request):
    req = get_params_from_request(request, new_device_request_schema)
    device_id = request.registry.device_mngr.add_device(project_name=request.matchdict['project_name'], **req)
    return {'uuid': device_id}


@get_view(route_name='device')
def get_device(request):
    return request.registry.device_mngr.get_device(request.matchdict['project_name'],
                                                   request.matchdict['device_id'])


@put_view(route_name='device')
def update_device(request):
    pass


@delete_view(route_name='device')
def delete_device(request):
    request.registry.device_mngr.delete_device_by_id(request.matchdict['project_name'], request.matchdict['device_id'])