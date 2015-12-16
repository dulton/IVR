from ivr.ivc.rest.common import get_view, post_view, put_view, delete_view
from ivr.ivc.rest.common import get_params_from_request
from ivr.common.schema import Schema, Optional, Default, BoolVal, EnumVal, Use


def includeme(config):
    # block device list resource
    # GET:    block device list
    config.add_route('live_stream', '/{vendor}/cameras/{camera_id}/live')
    config.add_route('live_stream_keepalive', '/{vendor}/cameras/{camera_id}/live/keepalive')


get_stream_schema = Schema({'format': EnumVal(['hls', 'rtmp']),
                            Optional('quality'): Default(EnumVal(['high', 'low']), default='low'),
                            Optional('keepalive_required'): Default(BoolVal(), default=False),
                            Optional('create'): Default(BoolVal(), default=True)})


@post_view(route_name='live_stream')
def request_live_stream(request):
    req = get_params_from_request(request, get_stream_schema)
    url, session_id = request.registry.stream_mgr.request_live_stream(request.matchdict['camera_id'],
                                                                      stream_format=req['format'],
                                                                      stream_quality=req['quality'],
                                                                      keepalive_required=req['keepalive_required'],
                                                                      create=req['create'])
    return {'url': url, 'session_id': session_id}


delete_stream_schema = Schema({Optional('session_id'): Use(str),
                               Optional('force'): Default(BoolVal(), default=False),})


@delete_view(route_name='live_stream')
def delete_live_stream(request):
    req = get_params_from_request(request, delete_stream_schema)
    request.registry.stream_mgr.delete_live_stream(request.matchdict['camera_id'],
                                                   session_id=req['session_id'],
                                                   force=req['force'])


keepalive_schema = Schema({'session_id': Use(str)})


@post_view(route_name='live_stream_keepalive')
def keepalive_live_stream(request):
    req = get_params_from_request(request, keepalive_schema)
    request.registry.stream_mgr.keepalive_live_stream(request.matchdict['camera_id'],
                                                      req['session_id'])


