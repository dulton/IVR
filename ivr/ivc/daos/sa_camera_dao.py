
from __future__ import unicode_literals, division
from .sa_models import SACamera
from ..manager.camera import Camera


class SACameraDao(object):
    def __init__(self, dao_context_mngr):
        self._dao_context_mngr = dao_context_mngr

    def get_by_uuid(self, uuid):
        pass

    def get_list_by_project(self, filter_name=None, filter_value="", project_name=None, start_index=0, max_number=65535):
        pass

    def get_count_by_project(self, filter_name=None, filter_value="", project_name=None):
        pass

    def add(self, camera):
        pass

    def delete_by_uuid(self, uuid):
        pass

    def update(self, camera):
        pass


def test_main():
    from .alchemy_dao_context_mngr import AlchemyDaoContextMngr
    from sqlalchemy import create_engine, dialects
    # import gevent
    # dialects.registry.register("sqlite", "streamswitch.wsgiapp.utils.sqlalchemy_gevent", "SqliteDialect")
    engine = create_engine("mysql+pymysql://test:123456@192.168.1.63/ivc_test", echo=True)

    dao_context_mngr = AlchemyDaoContextMngr(engine)
    camera_dao = SACameraDao(dao_context_mngr)
    # import pdb
    # pdb.set_trace()
    camera_list = camera_dao.get_list_by_project()
    camera_count = camera_dao.get_count_by_project()
    print("camera list (%d) at begin:" % camera_count)
    print(camera_list)

    camera = Camera("test_project", uuid="8d470ebc-a6c8-426e-88e9-7351752ab98b")

    # stream_conf_dao.del_stream_conf("test_name")
    camera_dao.add(camera)

    camera_list = camera_dao.get_list_by_project()
    camera_count = camera_dao.get_count_by_project()
    print("camera list (%d) after add:" % camera_count)
    print(camera_list)

    camera = camera_dao.get_by_uuid("8d470ebc-a6c8-426e-88e9-7351752ab98b")
    camera.desc = "abc"
    camera_dao.update(camera)

    camera_test = camera_dao.get_by_uuid("8d470ebc-a6c8-426e-88e9-7351752ab98b")
    assert(camera_test.desc == camera.desc)


    camera_dao.delete_by_uuid("8d470ebc-a6c8-426e-88e9-7351752ab98b")
    camera_list = camera_dao.get_list_by_project()
    camera_count = camera_dao.get_count_by_project()
    print("camera list (%d) after del:" % camera_count)
    print(camera_list)


