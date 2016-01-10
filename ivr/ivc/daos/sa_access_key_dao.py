
from __future__ import unicode_literals, division
from .sa_models import SAAccessKey
from ..manager.access_key import AccessKey

from ...common.exception import IVRError


class SAAccessKeyDao(object):
    def __init__(self, dao_context_mngr):
        self._dao_context_mngr = dao_context_mngr

    def get_by_key_id(self, key_id):
        with self._dao_context_mngr.context() as context:
            # in a transaction
            session = context.session
            sa_access_key = session.query(SAAccessKey).filter(SAAccessKey.key_id == key_id).one_or_none()
            if sa_access_key is None:
                return None
            access_key = sa_access_key.to_access_key(AccessKey)
        return access_key

    def get_list(self, key_type=None, username=None, start_index=0, max_number=65535):
        access_key_list = []
        with self._dao_context_mngr.context() as context:
            # in a transaction
            session = context.session
            query = session.query(SAAccessKey)
            if username is not None and len(username) != 0:
                query = query.filter(SAAccessKey.username == username)
            if key_type is not None:
                query = query.filter(SAAccessKey.key_type == key_type)
            for sa_access_key in query[start_index:max_number]:
                access_key = sa_access_key.to_access_key(AccessKey)
                access_key_list.append(access_key)
        return access_key_list

    def get_count(self, key_type=None, username=None):
        with self._dao_context_mngr.context() as context:
            # in a transaction
            session = context.session
            query = session.query(SAAccessKey)
            if username is not None and len(username) != 0:
                query = query.filter(SAAccessKey.username == username)
            if key_type is not None:
                query = query.filter(SAAccessKey.key_type == key_type)
            cnt = query.count()
        return cnt


    def add(self, access_key):
        with self._dao_context_mngr.context() as context:
            # in a transaction
            session = context.session
            sa_access_key = SAAccessKey()
            sa_access_key.from_access_key(access_key)
            session.add(sa_access_key)

    def delete_by_key_id(self, key_id):
        with self._dao_context_mngr.context() as context:
            # in a transaction
            session = context.session
            sa_access_key = session.query(SAAccessKey).filter(SAAccessKey.key_id == key_id).one_or_none()
            if sa_access_key is None:
                return
            session.delete(sa_access_key)

    def update(self, access_key):
        with self._dao_context_mngr.context() as context:
            # in a transaction
            session = context.session
            sa_access_key = session.query(SAAccessKey).filter(SAAccessKey.key_id == access_key.key_id).one()
            sa_access_key.from_access_key(access_key)



def test_main():
    from .sa_dao_context_mngr import AlchemyDaoContextMngr
    from sqlalchemy import create_engine
    from .sa_project_dao import SAProjectDao
    from .sa_user_dao import SAUserDao
    from ..manager.user import User
    # import gevent
    # dialects.registry.register("sqlite", "streamswitch.wsgiapp.utils.sqlalchemy_gevent", "SqliteDialect")
    engine = create_engine("mysql+pymysql://test:123456@127.0.0.1/ivc_test", echo=True)

    dao_context_mngr = AlchemyDaoContextMngr(engine)
    access_key_dao = SAAccessKeyDao(dao_context_mngr)
    user_dao = SAUserDao(dao_context_mngr)
    # import pdb
    # pdb.set_trace()
    with dao_context_mngr.context() as context:

        user = User(username="test_user", desc="test_user_desc")
        user_dao.add(user)

        access_key_list = access_key_dao.get_list(username="test_user")
        access_key_count = access_key_dao.get_count(username="test_user")
        print("access key list (%d) at begin:" % access_key_count)
        print(access_key_list)
        print(access_key_count == 0)


        access_key = AccessKey(key_id="test_key_id", secret="test_key_secret", username="test_user")
        access_key_dao.add(access_key)

        access_key_list = access_key_dao.get_list(username="test_user")
        access_key_count = access_key_dao.get_count(username="test_user")
        print("access key list (%d) after add:" % access_key_count)
        print(access_key_list)
        print(access_key_count == 1)

        access_key = access_key_dao.get_by_key_id("test_key_id")
        access_key.desc = "abc"
        access_key_dao.update(access_key)

        access_key_test = access_key_dao.get_by_key_id("test_key_id")
        assert(access_key_test.desc == access_key.desc)


        access_key_dao.delete_by_key_id("test_key_id")

        access_key_list = access_key_dao.get_list(username="test_user")
        access_key_count = access_key_dao.get_count(username="test_user")
        print("access key list (%d) after del:" % access_key_count)
        print(access_key_list)
        print(access_key_count == 0)

        user_dao.delete_by_username("test_user")
