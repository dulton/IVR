from ivr.ivc.rest.common import get_view, post_view, put_view, delete_view
from ivr.ivc.rest.common import get_params_from_request
from ivr.common.schema import Schema, Optional, Default, BoolVal, EnumVal, Use


def includeme(config):
    # block device list resource
    # GET:    block device list
    config.add_route('user_session_list', '/{project}/cameras/{camera_id}/session')
    config.add_route('user_session', '/{project}/cameras/{camera_id}/session/{sesion_id}')


@get_view(route_name='user_session_list')
def get_user_session_list(request):
    return {}


get_stream_schema = Schema({'format': EnumVal(['hls', 'rtmp']),
                            Optional('quality'): Default(EnumVal(['ld', 'sd', 'hd']), default='ld')})



@post_view(route_name='user_session_list')
def request_user_session(request):
    req = get_params_from_request(request, get_stream_schema)
    url, session_id = request.registry.session_mngr.request_session(request.matchdict['project'],
                                                                  request.matchdict['camera_id'],
                                                                  stream_format=req['format'],
                                                                  stream_quality=req['quality'],
                                                                  create=True)
    return {'url': url, 'session_id': session_id}


@delete_view(route_name='user_session')
def delete_user_session(request):
    request.registry.stream_mngr.delete_session(request.matchdict['project'],
                                                   request.matchdict['camera_id'],
                                                   request.matchdict['session_id'])



@post_view(route_name='user_session')
def keepalive_user_session(request):
    request.registry.stream_mngr.keepalive_session(request.matchdict['project'],
                                                      request.matchdict['camera_id'],
                                                      request.matchdict['session_id'])


