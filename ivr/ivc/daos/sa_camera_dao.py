
from __future__ import unicode_literals, division
from .sa_models import SACamera
from ..manager.camera import Camera


class SACameraDao(object):
    def __init__(self, dao_context_mngr):
        self._dao_context_mngr = dao_context_mngr

    def get_by_uuid(self, uuid):
        with self._dao_context_mngr.context() as context:
            # in a transaction
            session = context.session
            sa_camera = session.query(SACamera).filter(SACamera.uuid == uuid).one_or_none()
            if sa_camera is None:
                return None
            camera = sa_camera.to_camera(Camera)
        return camera

    def get_by_device_channel(self, device_uuid, channel_index):
        with self._dao_context_mngr.context() as context:
            # in a transaction
            session = context.session
            sa_camera = session.query(SACamera).filter(SACamera.device_uuid == device_uuid).filter(SACamera.channel_index == channel_index).one_or_none()
            if sa_camera is None:
                return None
            camera = sa_camera.to_camera(Camera)
        return camera

    def get_list(self, filter_name=None, filter_value="",
                 start_index=0, max_number=65535):
        return self.get_list_by_project(filter_name=filter_name, filter_value=filter_value,
                                        project_name=None,
                                        start_index=start_index, max_number=max_number)

    def get_list_by_project(self, filter_name=None, filter_value="", project_name=None,
                               start_index=0, max_number=65535):
        camera_list = []
        with self._dao_context_mngr.context() as context:
            # in a transaction
            session = context.session
            query = session.query(SACamera)
            if project_name is not None:
                query = query.filter(SACamera.project_name == project_name)
            if filter_name is not None and len(filter_name) != 0 and len(filter_value) != 0:
                query = query.filter(getattr(SACamera, filter_name).like("%"+filter_value+"%"))
            for sa_camera in query[start_index:max_number]:
                camera = sa_camera.to_camera(Camera)
                camera_list.append(camera)
        return camera_list

    def get_count(self, filter_name=None, filter_value=""):
        return self.get_count_by_project(filter_name=filter_name,
                                         filter_value=filter_value)

    def get_count_by_project(self, filter_name=None, filter_value="", project_name=None):
        with self._dao_context_mngr.context() as context:
            # in a transaction
            session = context.session
            query = session.query(SACamera)
            if project_name is not None:
                query = query.filter(SACamera.project_name == project_name)
            if filter_name is not None and len(filter_name) != 0 and len(filter_value) != 0:
                query = query.filter(getattr(SACamera, filter_name).like("%"+filter_value+"%"))
            cnt = query.count()
        return cnt

    def add(self, camera):
        with self._dao_context_mngr.context() as context:
            # in a transaction
            session = context.session
            sa_camera = SACamera()
            sa_camera.from_camera(camera)
            session.add(sa_camera)

    def delete_by_uuid(self, uuid):
        with self._dao_context_mngr.context() as context:
            # in a transaction
            session = context.session
            sa_camera = session.query(SACamera).filter(SACamera.uuid == uuid).one_or_none()
            if sa_camera is None:
                return
            session.delete(sa_camera)

    def update(self, camera):
        with self._dao_context_mngr.context() as context:
            # in a transaction
            session = context.session
            sa_camera = session.query(SACamera).filter(SACamera.uuid == camera.uuid).one()
            sa_camera.from_camera(camera)


def test_main():
    from .sa_dao_context_mngr import AlchemyDaoContextMngr
    from sqlalchemy import create_engine
    from ..manager.project import Project
    from .sa_project_dao import SAProjectDao
    from ..manager.device import Device
    from .sa_device_dao import SADeviceDao
    from ..manager.device import Device
    # import gevent
    # dialects.registry.register("sqlite", "streamswitch.wsgiapp.utils.sqlalchemy_gevent", "SqliteDialect")
    engine = create_engine("mysql+pymysql://test:123456@127.0.0.1/ivc_test", echo=True)



    dao_context_mngr = AlchemyDaoContextMngr(engine)
    camera_dao = SACameraDao(dao_context_mngr)
    project_dao = SAProjectDao(dao_context_mngr)
    device_dao = SADeviceDao(dao_context_mngr)
    # import pdb
    # pdb.set_trace()
    with dao_context_mngr.context() as context:

        project = Project(name="test_project", title="test_project_title",
                          desc="test_project_desc")
        project_dao.add(project)

        device = Device(project_name="test_project", uuid="f0769732-411e-4e93-942e-ae437ced2658",
                        name="test_device", desc="test_device_desc")

        device_dao.add(device)

        camera_list = camera_dao.get_list_by_project(project_name="test_project")
        camera_count = camera_dao.get_count_by_project(project_name="test_project")
        print("camera list (%d) at begin:" % camera_count)
        print(camera_list)

        camera = Camera("test_project", uuid="8d470ebc-a6c8-426e-88e9-7351752ab98b",
                        device_uuid="f0769732-411e-4e93-942e-ae437ced2658",
                        name="test_camera", desc="abc")

        # stream_conf_dao.del_stream_conf("test_name")
        camera_dao.add(camera)

        camera_list = camera_dao.get_list_by_project(filter_name="name", filter_value="t_c",
                                                     project_name="test_project")
        camera_count = camera_dao.get_count_by_project(filter_name="name", filter_value="t_c",
                                                     project_name="test_project")
        print("camera list (%d) after add:" % camera_count)
        print(camera_list)
        assert(camera_count == 1)

        camera = camera_dao.get_by_uuid("8d470ebc-a6c8-426e-88e9-7351752ab98b")
        camera.desc = "abc"
        camera_dao.update(camera)

        camera_test = camera_dao.get_by_uuid("8d470ebc-a6c8-426e-88e9-7351752ab98b")
        assert(camera_test.desc == camera.desc)


        camera_dao.delete_by_uuid("8d470ebc-a6c8-426e-88e9-7351752ab98b")
        camera_list = camera_dao.get_list_by_project(project_name="test_project")
        camera_count = camera_dao.get_count_by_project(project_name="test_project")
        print("camera list (%d) after del:" % camera_count)
        print(camera_list)
        assert(camera_count == 0)

        device_dao.delete_by_uuid("f0769732-411e-4e93-942e-ae437ced2658")

        project_dao.delete_by_name("test_project")


