# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division


class SAUserSessionLogDao(object):
    def __init__(self, dao_context_mngr):
        self._dao_context_mngr = dao_context_mngr

    def add(self, log):
        pass

    def update(self, log):
        pass

    def get_by_id(self, session_id):
        pass

    def get_list_by_project(self, project_name, filter_name=None, filter_value="",
                 start_from=None, end_to=None,
                 start_index=0, max_number=65535):
        pass

    def get_count_by_project(self, project_name, filter_name=None, filter_value="",
                             start_from=None, end_to=None):
        pass