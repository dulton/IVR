# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
import gevent
from ivr.common.exception import IVRError
import datetime
import hashlib
from ivr.common.utils import STRING

PASSWORD_PBKDF2_HMAC_SHA256_SALT = b'opensight.cn'

class User(object):
    USER_FLAG_PRIVILEGE = 0x1

    USER_TYPE_NORMAL = 0
    USER_TYPE_ADMIN = 1


    def __init__(self, username, password="", title="default", desc="", long_desc="",
                 flags=0, cellphone="", email="", user_type=USER_TYPE_NORMAL,
                 ctime=None, utime=None, ltime=None):
        self.username = username
        self.password = password
        self.title = title
        self.desc = desc
        self.long_desc = long_desc
        self.flags = flags
        self.cellphone = cellphone
        self.email = email
        self.user_type = user_type
        if ctime is None or utime is None or ltime is None:
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
        if ltime is None:
            self.ltime = now
        else:
            self.ltime = ltime

    def __str__(self):
        return 'User "{0}"'.format(self.username)

    def __json__(self):
        obj_dict = {}
        for k, v in self.__dict__.items():
            if not k.startswith('_'):
                obj_dict[k] = v
        obj_dict.pop("password")
        return obj_dict


class UserManager(object):
    def __init__(self, user_dao=None, project_dao=None, dao_context_mngr=None):
        self._user_dao = user_dao
        self._project_dao = project_dao
        self._dao_context_mngr =dao_context_mngr

    def get_user_list_in_pages(self, filter_name=None, filter_value="", start_index=0, max_number=65535):
        with self._dao_context_mngr.context():
            user_list = self._user_dao.get_list(
                filter_name=filter_name,
                filter_value=filter_value,
                start_index=start_index,
                max_number=max_number)
            user_total_count = self._user_dao.get_count(
                filter_name=filter_name,
                filter_value=filter_value)
        return user_total_count, user_list

    def get_user_list_in_project(self, project_name,
                                    filter_name=None, filter_value="",
                                     start_index=0, max_number=65535):
        with self._dao_context_mngr.context():

            project = self._project_dao.get_by_name(project_name)
            if project is None:
                raise IVRError("Project(%s) Not Found" % project_name, 404)

            user_list = self._user_dao.get_list_by_project(
                project_name=project_name,
                filter_name=filter_name,
                filter_value=filter_value,
                start_index=start_index,
                max_number=max_number)
            user_total_count = self._user_dao.get_count_by_project(
                project_name=project_name,
                filter_name=filter_name,
                filter_value=filter_value)
        return user_total_count, user_list

    def get_user(self, username):
        with self._dao_context_mngr.context():
            user = self._user_dao.get_by_username(username)
            if user is None:
                raise IVRError("User Not Found", 404)
        return user

    def add_user(self, username, password, **kwargs):
        with self._dao_context_mngr.context():
            user = self._user_dao.get_by_username(username)
            if user is not None:
                raise IVRError("Username Exist", 400)
            password = STRING(hashlib.sha256(password.encode()).hexdigest())
            user = User(username=username, password=password, **kwargs)

            self._user_dao.add(user)
            user = self._user_dao.get_by_username(username)
        return user

    def mod_user(self, username,  **kwargs):
        with self._dao_context_mngr.context():
            user = self._user_dao.get_by_username(username)
            if user is None:
                raise IVRError("User Not Found", 404)
            for (k, v) in kwargs.items():
                if k in ("title", "desc", "long_desc", "cellphone", "email"):
                    setattr(user, k, v)
            user.utime = datetime.datetime.now()
            self._user_dao.update(user)
        return user

    def change_password(self, username, old_password, new_password):
        with self._dao_context_mngr.context():
            user = self._user_dao.get_by_username(username)
            if user is None:
                raise IVRError("User Not Found", 404)
            if user.password != hashlib.sha256(old_password).hexdigest():
                raise IVRError("Old password mismatch", 404)
            user.password = STRING(hashlib.sha256(new_password.encode()).hexdigest())
            user.utime = datetime.datetime.now()
            self._user_dao.update(user)

    def reset_password(self, username, new_password):
        with self._dao_context_mngr.context():
            user = self._user_dao.get_by_username(username)
            if user is None:
                raise IVRError("User Not Found", 404)
            user.password = STRING(hashlib.sha256(new_password.encode()).hexdigest())
            user.utime = datetime.datetime.now()
            self._user_dao.update(user)

    def delete_user_by_name(self, username):
        with self._dao_context_mngr.context():
            user = self._user_dao.get_by_username(username)
            if user is None:
                raise IVRError("Username Not Found", 404)
            self._user_dao.delete_by_username(username)

    def get_user_projects(self, username):
        with self._dao_context_mngr.context():
            user = self._user_dao.get_by_username(username)
            if user is None:
                raise IVRError("Username Not Found", 404)
            return self._user_dao.get_user_projects(user)

    def join_to_project(self, username, project_name):
        with self._dao_context_mngr.context():
            user = self._user_dao.get_by_username(username)
            if user is None:
                raise IVRError("Username Not Found", 404)

            user_projects = self._user_dao.get_user_projects(user)
            for user_project in user_projects:
                if user_project.name == project_name:
                    raise IVRError("Already in Project", 400)

            project = self._project_dao.get_by_name(project_name)
            if project is None:
                raise IVRError("Project(%s) Not Found" % project_name, 404)
            self._user_dao.join_to_project(user, project)

    def leave_from_project(self, username, project_name):
        with self._dao_context_mngr.context():
            user = self._user_dao.get_by_username(username)
            if user is None:
                raise IVRError("Username Not Found", 404)
            user_projects = self._user_dao.get_user_projects(user)
            for user_project in user_projects:
                if user_project.name == project_name:
                    break
            else:
                raise IVRError("Not In Project", 400)
            self._user_dao.leave_from_project(user, user_project)

    def login(self, username, password):
        # return a JWT for this user with the privilege
        pass
