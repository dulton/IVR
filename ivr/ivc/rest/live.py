from ivr.common.rest import get_view, post_view, put_view, delete_view
from ivr.common.rest import get_params_from_request
from ivr.common.schema import Schema, Optional, Default, BoolVal


def includeme(config):
    # block device list resource
    # GET:    block device list
    config.add_route('live_stream', '/cameras/<camera_id>/live/<format>')
    config.add_route('live_stream_keepalive', '/cameras/<camera_id>/live/<format>/keepalive')


get_stream_schema = Schema({Optional('keepalive_required'): Default(BoolVal(), default=False),
                            Optional('create'): Default(BoolVal(), default=True)})


@post_view(route_name='live_stream')
def request_live_stream(request):
    req = get_params_from_request(request, get_stream_schema)
    url = request.registry.stream_mgr.request_live_stream(request.matchdict['camera_id'],
                                                          request.matchdict['format'],
                                                          keepalive_required=req['keepalive_required'],
                                                          create=req['create'])
    return {'url': url}


delete_stream_schema = Schema({Optional('force'): Default(BoolVal(), default=False),})


@delete_view(route_name='live_stream')
def delete_live_stream(request):
    req = get_params_from_request(request, delete_stream_schema)
    request.registry.stream_mgr.delete_live_stream(request.matchdict['camera_id'],
                                                   request.matchdict['format'],
                                                   req['force'])


@post_view(route_name='live_stream_keepalive')
def keepalive_live_stream(request):
    request.registry.stream_mgr.keepalive_live_stream(request.matchdict['camera_id'], request.matchdict['format'])


