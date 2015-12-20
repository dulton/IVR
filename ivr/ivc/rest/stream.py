from ivr.ivc.rest.common import get_view, post_view, put_view, delete_view
from ivr.ivc.rest.common import get_params_from_request
from ivr.common.datatype import VideoQuality
from ivr.common.schema import Schema, BoolVal, Default, Optional


def includeme(config):
    config.add_route('stream_list', '/{project}/cameras/{camera_id}/streams')
    config.add_route('stream', '/{project}/cameras/{camera_id}/streams/{stream_id}')


@get_view(route_name='stream_list')
def get_stream_list(request):
    req = get_params_from_request(request)
    return {}


start_stream_schema = Schema({
    'quality': VideoQuality.schema,
    Optional('autodelete'): Default(BoolVal(), default=True)
})


@post_view(route_name='stream_list')
def start_stream(request):
    req = get_params_from_request(request, start_stream_schema)



@get_view(route_name='stream')
def get_stream_info(request):
    return {}


@delete_view(route_name='stream')
def stop_stream(request):
    return