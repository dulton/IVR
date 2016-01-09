
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

    def get_list(self, start_index=0, max_number=65535):
        access_key_list = []
        with self._dao_context_mngr.context() as context:
            # in a transaction
            session = context.session
            query = session.query(SAAccessKey)
            for sa_access_key in query[start_index:max_number]:
                access_key = sa_access_key.to_user(AccessKey)
                access_key_list.append(access_key)
        return access_key_list

    def get_count(self):
        with self._dao_context_mngr.context() as context:
            # in a transaction
            session = context.session
            query = session.query(SAAccessKey)
            cnt = query.count()
        return cnt

    def get_list_by_username(self, username):
        access_key_list = []
        with self._dao_context_mngr.context() as context:
            # in a transaction
            session = context.session
            query = session.query(SAAccessKey)
            if username is not None:
                query = query.filter(SAAccessKey.username == username)
            for sa_access_key in query:
                access_key = sa_access_key.to_user(AccessKey)
                access_key_list.append(access_key)
        return access_key_list

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
            sa_access_key.from_user(access_key)



def test_main():
    from .sa_dao_context_mngr import AlchemyDaoContextMngr
    from sqlalchemy import create_engine
    from .sa_project_dao import SAProjectDao
    from ..manager.project import Project
    # import gevent
    # dialects.registry.register("sqlite", "streamswitch.wsgiapp.utils.sqlalchemy_gevent", "SqliteDialect")
    engine = create_engine("mysql+pymysql://test:123456@127.0.0.1/ivc_test", echo=True)

    dao_context_mngr = AlchemyDaoContextMngr(engine)
    user_dao = SAUserDao(dao_context_mngr)
    project_dao = SAProjectDao(dao_context_mngr)
    # import pdb
    # pdb.set_trace()
    with dao_context_mngr.context() as context:

        project = Project(name="test_project", title="test_project_title",
                          desc="test_project_desc")
        project_dao.add(project)

        user_list = user_dao.get_list_by_project(project_name="test_project")
        user_count = user_dao.get_count_by_project(project_name="test_project")
        print("user list (%d) at begin:" % user_count)
        print(user_list)
        assert(user_count == 0)

        user = User(username="test_user", desc="test_user_desc")
        user_dao.add(user)

        user_dao.join_to_project(user, project)

        user_list = user_dao.get_list_by_project(filter_name="username", filter_value="t_u",
                                                    project_name="test_project")
        user_count = user_dao.get_count_by_project(filter_name="username", filter_value="t_u",
                                                    project_name="test_project")
        print("user list (%d) after add:" % user_count)
        print(user_list)
        assert(user_count == 1)

        project_list = user_dao.get_user_projects(user)
        print("project list (%d) for user %s after join:" % (len(project_list), user.username))
        print(project_list)
        assert(len(project_list) == 1)

        user = user_dao.get_by_username("test_user")
        user.desc = "abc"
        user_dao.update(user)

        user_test = user_dao.get_by_username("test_user")
        assert(user_test.desc == user.desc)

        user_dao.leave_from_project(user, project)
        project_list = user_dao.get_user_projects(user)
        print("project list (%d) for user %s after leave:" % (len(project_list), user.username))
        print(project_list)
        assert(len(project_list) == 0)

        user_dao.delete_by_username("test_user")

        user_list = user_dao.get_list_by_project(project_name="test_project")
        user_count = user_dao.get_count_by_project(project_name="test_project")
        print("user list (%d) after del:" % user_count)
        print(user_list)
        assert(user_count == 0)

        project_dao.delete_by_name("test_project")
