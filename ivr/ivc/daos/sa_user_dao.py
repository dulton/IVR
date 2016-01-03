
from __future__ import unicode_literals, division
from .sa_models import SAUser, SAProject
from ..manager.user import User
from ..manager.project import Project
from ...common.exception import IVRError


class SAUserDao(object):
    def __init__(self, dao_context_mngr):
        self._dao_context_mngr = dao_context_mngr

    def get_by_username(self, name):
        with self._dao_context_mngr.context() as context:
            # in a transaction
            session = context.session
            sa_user = session.query(SAUser).filter(SAUser.username == name).one_or_none()
            if sa_user is None:
                return None
            user = sa_user.to_user(User)
        return user

    def get_list(self, filter_name=None, filter_value="",
                   start_index=0, max_number=65535):
        return self.get_list_by_project(filter_name=filter_name, filter_value=filter_value,
                                        project_name=None,
                                        start_index=start_index, max_number=max_number)

    def get_count(self, filter_name=None, filter_value=""):
        return self.get_count_by_project(filter_name=filter_name, filter_value=filter_value,
                                         project_name=None)

    def get_list_by_project(self, filter_name=None, filter_value="", project_name=None,
                               start_index=0, max_number=65535):
        user_list = []
        with self._dao_context_mngr.context() as context:
            # in a transaction
            session = context.session
            query = session.query(SAUser)
            if project_name is not None:
                query = query.filter(SAUser.projects.any(SAProject.name == project_name))
            if filter_name is not None and len(filter_name) != 0 and len(filter_value) != 0:
                query = query.filter(getattr(SAUser, filter_name).like("%"+filter_value+"%"))
            for sa_user in query[start_index:max_number]:
                user = sa_user.to_user(User)
                user_list.append(user)
        return user_list

    def get_count_by_project(self, filter_name=None, filter_value="", project_name=None):
        with self._dao_context_mngr.context() as context:
            # in a transaction
            session = context.session
            query = session.query(SAUser)
            if project_name is not None:
                query = query.filter(SAUser.projects.any(SAProject.name == project_name))
            if filter_name is not None and len(filter_name) != 0 and len(filter_value) != 0:
                query = query.filter(getattr(SAUser, filter_name).like("%"+filter_value+"%"))
            cnt = query.count()
        return cnt

    def get_user_projects(self, user):
        project_list = []
        with self._dao_context_mngr.context() as context:
            # in a transaction
            session = context.session
            sa_user = session.query(SAUser).filter(SAUser.username == user.username).one()
            for sa_project in sa_user.projects:
                project = sa_project.to_project(Project)
                project_list.append(project)
        return project_list

    def join_to_project(self, user, project):
        with self._dao_context_mngr.context() as context:
            # in a transaction
            session = context.session
            sa_user = session.query(SAUser).filter(SAUser.username == user.username).one()
            sa_project = session.query(SAProject).filter(SAProject.name == project.name).one()
            sa_user.projects.append(sa_project)

    def leave_from_project(self, user, project):
        with self._dao_context_mngr.context() as context:
            # in a transaction
            session = context.session
            sa_user = session.query(SAUser).filter(SAUser.username == user.username).one()
            sa_project = session.query(SAProject).filter(SAProject.name == project.name).one()
            if sa_project not in sa_user.projects:
                raise IVRError("user (%s) not in project (%s)" % (user.username, project.name), 400)
            sa_user.projects.remove(sa_project)

    def add(self, user):
        with self._dao_context_mngr.context() as context:
            # in a transaction
            session = context.session
            sa_user = SAUser()
            sa_user.from_user(user)
            session.add(sa_user)

    def delete_by_username(self, username):
        with self._dao_context_mngr.context() as context:
            # in a transaction
            session = context.session
            sa_user = session.query(SAUser).filter(SAUser.username == username).one_or_none()
            if sa_user is None:
                return
            session.delete(sa_user)

    def update(self, user):
        with self._dao_context_mngr.context() as context:
            # in a transaction
            session = context.session
            sa_user = session.query(SAUser).filter(SAUser.username == user.username).one()
            sa_user.from_user(user)


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
