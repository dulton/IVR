from ivr.common.rest import get_view, post_view, put_view, delete_view
from ivr.common.rest import get_params_from_request
from pyramid.view import view_config


def includeme(config):
    # block device list resource
    # GET:    block device list
    config.add_route('camera_list', '/cameras')
    config.add_route('camera', '/cameras/{camera}')

"""
def preflight_handler(request):
    return {'ok': 'nice'}


class _rest_view(view_config):
    def __init__(self, **settings):
        method = self.__class__.__name__.split('_')[0].upper()
        super(_rest_view, self).__init__(request_method=method,
                                         **settings)
        view_config(request_method='POST', route_name=settings['route_name'])(preflight_handler)


class get_view(_rest_view):
    pass
"""

@get_view(route_name='camera_list')
def get_camera_list(request):
    return {'c01': {'ip': '1.2.3.4'}, 'c02': {'ip': '3.4.5.6'}}


@get_view(route_name='camera')
def get_camera(request):
    return {'c01': {'ip': '1.2.3.4'}}


@post_view(route_name='camera')
def post_camera(request):
    return {'post': 'ok'}

