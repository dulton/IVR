
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
            camera = Camera(project_name=sa_camera.project_name,
                            uuid=sa_camera.uuid,
                            device_uuid=sa_camera.device_uuid,
                            channel_index=sa_camera.channel_index,
                            name=sa_camera.name,
                            flags=sa_camera.flags,
                            is_online=sa_camera.is_online,
                            desc=sa_camera.desc,
                            long_desc=sa_camera.long_desc,
                            longitude=sa_camera.longitude,
                            latitude=sa_camera.latitude,
                            altitude=sa_camera.altitude,
                            ctime=sa_camera.ctime,
                            utime=sa_camera.utime)
        return camera

    def get_list_by_project(self, filter_name=None, filter_value="", project_name=None,
                                start_index=0, max_number=65535):
        camera_list = []
        with self._dao_context_mngr.context() as context:
            # in a transaction
            session = context.session
            query = session.query(SACamera)
            if project_name is not None:
                query = query.filter(SACamera.project_name == project_name)
            if filter_name is not None:
                query = query.filter(getattr(SACamera, filter_name).like("%"+filter_value+"%"))
            for sa_camera in query[start_index, max_number]:
                camera = Camera(project_name=sa_camera.project_name,
                                uuid=sa_camera.uuid,
                                device_uuid=sa_camera.device_uuid,
                                channel_index=sa_camera.channel_index,
                                name=sa_camera.name,
                                flags=sa_camera.flags,
                                is_online=sa_camera.is_online,
                                desc=sa_camera.desc,
                                long_desc=sa_camera.long_desc,
                                longitude=sa_camera.longitude,
                                latitude=sa_camera.latitude,
                                altitude=sa_camera.altitude,
                                ctime=sa_camera.ctime,
                                utime=sa_camera.utime)
                camera_list.append(camera)
        return camera_list

    def get_count_by_project(self, filter_name=None, filter_value="", project_name=None):
        with self._dao_context_mngr.context() as context:
            # in a transaction
            session = context.session
            query = session.query(SACamera)
            if project_name is not None:
                query = query.filter(SACamera.project_name == project_name)
            if filter_name is not None:
                query = query.filter(getattr(SACamera, filter_name).like("%"+filter_value+"%"))
            cnt = query.count()
        return cnt

    def add(self, camera):
        with self._dao_context_mngr.context() as context:
            # in a transaction
            session = context.session
            sa_camera = SACamera(
                uuid=camera.uuid,
                device_uuid=camera.device_uuid,
                channel_index=camera.channel_index,
                name=camera.name,
                flags=camera.flags,
                is_online=camera.is_online,
                desc=camera.desc,
                long_desc=camera.long_desc,
                longitude=camera.longitude,
                latitude=camera.latitude,
                altitude=camera.altitude,
                project_name=camera.project_name,
                ctime=camera.ctime,
                utime=camera.utime)
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


