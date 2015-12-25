
from __future__ import unicode_literals, division
from .sa_models import SADevice


class SADeviceDao(object):
    def __init__(self, dao_context_mngr):
        self._dao_context_mngr = dao_context_mngr

    def get_by_uuid(self, uuid):
        pass

    def get_list_by_project(self, filter_name=None, filter_value="", project_name=None, start_index=0, max_number=65535):
        pass

    def get_count_by_project(self, filter_name=None, filter_value="", project_name=None):
        pass

    def add(self, dev):
        pass

    def delete_by_uuid(self, uuid):
        pass

    def update(self, dev):
        pass



def test_main():
    from .alchemy_dao_context_mngr import AlchemyDaoContextMngr
    from sqlalchemy import create_engine, dialects
    # import gevent
    # dialects.registry.register("sqlite", "streamswitch.wsgiapp.utils.sqlalchemy_gevent", "SqliteDialect")
    engine = create_engine("mysql+pymysql://test:123456@192.168.1.63/ivc_test",echo=True)

    dao_context_mngr = AlchemyDaoContextMngr(engine)
    stream_conf_dao = SACameraDao(dao_context_mngr)
    # import pdb
    # pdb.set_trace()
    stream_conf_list = stream_conf_dao.get_all_stream_conf()
    print("stream confs at begin:")
    print(stream_conf_list)
    stream_conf = StreamConf("test_type", "test_name", "test://test")
    # stream_conf_dao.del_stream_conf("test_name")
    stream_conf_dao.add_stream_conf(stream_conf)
    stream_conf_list = stream_conf_dao.get_all_stream_conf()
    print("stream confs after add:")
    print(stream_conf_list)
    stream_conf_dao.del_stream_conf("test_name")
    stream_conf_list = stream_conf_dao.get_all_stream_conf()
    print("stream confs after del:")
    print(stream_conf_list)


