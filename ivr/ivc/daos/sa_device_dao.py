
from __future__ import unicode_literals, division
from .sa_models import SADevice
from ..manager.device import Device


class SADeviceDao(object):
    def __init__(self, dao_context_mngr):
        self._dao_context_mngr = dao_context_mngr

    def get_by_uuid(self, uuid):
        with self._dao_context_mngr.context() as context:
            # in a transaction
            session = context.session
            sa_device = session.query(SADevice).filter(SADevice.uuid == uuid).one_or_none()
            if sa_device is None:
                return None
            device = sa_device.to_device(Device)
        return device

    def get_list_by_project(self, filter_name=None, filter_value="", project_name=None, start_index=0, max_number=65535):
        device_list = []
        with self._dao_context_mngr.context() as context:
            # in a transaction
            session = context.session
            query = session.query(SADevice)
            if project_name is not None:
                query = query.filter(SADevice.project_name == project_name)
            if filter_name is not None:
                query = query.filter(getattr(SADevice, filter_name).like("%"+filter_value+"%"))
            for sa_device in query[start_index:max_number]:
                device = sa_device.to_device(SADevice)
                device_list.append(device)
        return device_list

    def get_count_by_project(self, filter_name=None, filter_value="", project_name=None):
        with self._dao_context_mngr.context() as context:
            # in a transaction
            session = context.session
            query = session.query(SADevice)
            if project_name is not None:
                query = query.filter(SADevice.project_name == project_name)
            if filter_name is not None:
                query = query.filter(getattr(SADevice, filter_name).like("%"+filter_value+"%"))
            cnt = query.count()
        return cnt

    def add(self, dev):
        with self._dao_context_mngr.context() as context:
            # in a transaction
            session = context.session
            sa_device = SADevice()
            sa_device.from_device(dev)
            session.add(sa_device)

    def delete_by_uuid(self, uuid):
        with self._dao_context_mngr.context() as context:
            # in a transaction
            session = context.session
            sa_camera = session.query(SADevice).filter(SADevice.uuid == uuid).one_or_none()
            if sa_camera is None:
                return
            session.delete(sa_camera)

    def update(self, dev):
        with self._dao_context_mngr.context() as context:
            # in a transaction
            session = context.session
            sa_device = session.query(SADevice).filter(SADevice.uuid == dev.uuid).one()
            sa_device.from_device(dev)



def test_main():
    from .sa_dao_context_mngr import AlchemyDaoContextMngr
    from sqlalchemy import create_engine
    from .sa_project_dao import SAProjectDao
    from ..manager.project import Project
    # import gevent
    # dialects.registry.register("sqlite", "streamswitch.wsgiapp.utils.sqlalchemy_gevent", "SqliteDialect")
    engine = create_engine("mysql+pymysql://test:123456@127.0.0.1/ivc_test", echo=True)



    dao_context_mngr = AlchemyDaoContextMngr(engine)
    device_dao = SADeviceDao(dao_context_mngr)
    project_dao = SAProjectDao(dao_context_mngr)
    # import pdb
    # pdb.set_trace()
    with dao_context_mngr.context() as context:

        project = Project(name="test_project", title="test_project_title",
                          desc="test_project_desc")

        project_dao.add(project)

        device_list = device_dao.get_list_by_project(project_name="test_project")
        device_count = device_dao.get_count_by_project(project_name="test_project")
        print("device list (%d) at begin:" % device_count)
        print(device_list)

        device = Device(project_name="test_project", uuid="f0769732-411e-4e93-942e-ae437ced2658",
                        name="test_device", desc="test_device_desc")

        device_dao.add(device)

        device_list = device_dao.get_list_by_project(filter_name="name", filter_value="t_d",
                                                     project_name="test_project")
        device_count = device_dao.get_count_by_project(filter_name="name", filter_value="t_d",
                                                      project_name="test_project")
        print("device list (%d) after add:" % device_count)
        print(device_list)
        assert(device_count == 1)

        device = device_dao.get_by_uuid("f0769732-411e-4e93-942e-ae437ced2658")
        device.desc = "abc"
        device_dao.update(device)

        device_test = device_dao.get_by_uuid("f0769732-411e-4e93-942e-ae437ced2658")
        assert(device_test.desc == device.desc)

        device_dao.delete_by_uuid("f0769732-411e-4e93-942e-ae437ced2658")
        device_list = device_dao.get_list_by_project(project_name="test_project")
        device_count = device_dao.get_count_by_project(project_name="test_project")
        print("device list (%d) after del:" % device_count)
        print(device_list)
        assert(device_count == 0)

        project_dao.delete_by_name("test_project")
