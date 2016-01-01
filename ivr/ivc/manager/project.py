# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
import gevent
from ivr.common.exception import IVRError
import datetime


class Project(object):

    def __init__(self, name, title="default", desc="", long_desc="",
                 max_media_sessions=0,
                 ctime=None, utime=None):
        self.name = name
        self.title = title
        self.desc = desc
        self.long_desc = long_desc
        self.max_media_sessions = max_media_sessions
        if ctime is None or utime is None:
            now = datetime.datetime.now()
        else:
            now = 0
        if ctime is None:
            self.ctime = now
        else:
            self.ctime = ctime
        if utime is None:
            self.utime = now
        else:
            self.utime = utime

    def __str__(self):
        return 'project <{0}>'.format(self.name)


class ProjectManager(object):
    def __init__(self, project_dao):
        self._dao = project_dao

    def add_project(self, project_name, *args, **kwargs):
        project = Project(project_name, *args, **kwargs)
        print project.__dict__
        self._dao.add(project)

    def delete_project(self, project):
        self._dao.delete_by_name(project.name)

    def delete_project_by_name(self, project_name):
        project = self._dao.get_by_name(project_name)
        if project:
            self._dao.delete_by_name(project_name)

    def get_project(self, project_name):
        return self._dao.get_by_name(project_name)

    def get_project_list(self, start, limit):
        return self._dao.get_list(start_index=start, max_number=limit)

    def get_project_count(self):
        return self._dao.get_count()