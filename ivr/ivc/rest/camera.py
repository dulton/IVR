from ivr.ivc.rest.common import get_view, post_view, put_view, delete_view
from ivr.ivc.rest.common import get_params_from_request
from ivr.common.schema import Schema, Optional, Default, IntVal


def includeme(config):
    # block device list resource
    # GET:    block device list
    config.add_route('camera_list', '/{vendor}/cameras')
    config.add_route('camera', '/{vendor}/cameras/{camera_id}')


get_cameras_list_schema = Schema({Optional('start'): Default(IntVal(min=0), default=0),
                                  Optional('limit'): Default(IntVal(min=0, max=100), default=20)})


@get_view(route_name='camera_list')
def get_camera_list(request):
    req = get_params_from_request(request, get_cameras_list_schema)
    start = req['start']
    limit = req['limit']
    total = len(request.registry.camera_mgr)
    resp = {'total': total,
            'start': req['start'],
            'list': []}
    if limit > 0 and start < total:
        index = 0
        for camera in request.registry.camera_mgr.iter_camera():
            if index >= start:
                if index < start+limit:
                    resp['list'].append(camera)
                else:
                    break
    return resp


@get_view(route_name='camera')
def get_camera(request):
    return request.registry.camera_mgr.get_camera(request.matchdict['camera_id'])


