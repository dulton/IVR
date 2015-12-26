
from __future__ import unicode_literals, division
from .sa_models import SAProject
from ..manager.project import Project


class SAProjectDao(object):
    def __init__(self, dao_context_mngr):
        self._dao_context_mngr = dao_context_mngr

    def get_by_name(self, name):
        with self._dao_context_mngr.context() as context:
            # in a transaction
            session = context.session
            sa_project = session.query(SAProject).filter(SAProject.name == name).one_or_none()
            if sa_project is None:
                return None
            project = sa_project.to_project(Project)
        return project

    def get_list(self, filter_name=None, filter_value="",
                   start_index=0, max_number=65535):
        project_list = []
        with self._dao_context_mngr.context() as context:
            # in a transaction
            session = context.session
            query = session.query(SAProject)
            if filter_name is not None:
                query = query.filter(getattr(SAProject, filter_name).like("%"+filter_value+"%"))
            for sa_project in query[start_index:max_number]:
                project = sa_project.to_project(Project)
                project_list.append(project)
        return project_list

    def get_count(self, filter_name=None, filter_value="", project_name=None):
        with self._dao_context_mngr.context() as context:
            # in a transaction
            session = context.session
            query = session.query(SAProject)
            if filter_name is not None:
                query = query.filter(getattr(SAProject, filter_name).like("%"+filter_value+"%"))
            cnt = query.count()
        return cnt

    def add(self, project):
        with self._dao_context_mngr.context() as context:
            # in a transaction
            session = context.session
            sa_project = SAProject()
            sa_project.from_project(project)
            session.add(sa_project)

    def delete_by_name(self, name):
        with self._dao_context_mngr.context() as context:
            # in a transaction
            session = context.session
            sa_camera = session.query(SAProject).filter(SAProject.name == name).one_or_none()
            if sa_camera is None:
                return
            session.delete(sa_camera)

    def update(self, project):
        with self._dao_context_mngr.context() as context:
            # in a transaction
            session = context.session
            sa_project = session.query(SAProject).filter(SAProject.name == project.name).one()
            sa_project.from_project(project)


def test_main():
    from .sa_dao_context_mngr import AlchemyDaoContextMngr
    from sqlalchemy import create_engine
    # import gevent
    # dialects.registry.register("sqlite", "streamswitch.wsgiapp.utils.sqlalchemy_gevent", "SqliteDialect")
    engine = create_engine("mysql+pymysql://test:123456@127.0.0.1/ivc_test", echo=True)


    dao_context_mngr = AlchemyDaoContextMngr(engine)
    project_dao = SAProjectDao(dao_context_mngr)
    # import pdb
    # pdb.set_trace()
    with dao_context_mngr.context() as context:
        project_list = project_dao.get_list()
        project_count = project_dao.get_count()
        print("project list (%d) at begin:" % project_count)
        print(project_list)

        project = Project(name="test_project", title="test_project_title",
                          desc="test_project_desc")

        project_dao.add(project)

        project_list = project_dao.get_list(filter_name="name", filter_value="t_p")
        project_count = project_dao.get_count(filter_name="name", filter_value="t_p")
        print("project list (%d) after add:" % project_count)
        print(project_list)
        assert(project_count == 1)

        project = project_dao.get_by_name("test_project")
        project.desc = "abc"
        project_dao.update(project)

        camera_test = project_dao.get_by_name("test_project")
        assert(camera_test.desc == project.desc)

        project_dao.delete_by_name("test_project")
        project_list = project_dao.get_list()
        project_count = project_dao.get_count()
        print("project list (%d) after del:" % project_count)
        print(project_list)
        assert(project_count == 0)


