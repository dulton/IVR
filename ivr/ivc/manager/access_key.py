# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
import gevent
from ivr.common.exception import IVRError
from .user import User
import datetime
import random
import base64
import sys

class AccessKey(object):
    KEY_TYPE_PRIVILEGE = 0x1
    KEY_TYPE_NORMAL = 0

    def __init__(self, key_id, secret, username, key_type=KEY_TYPE_NORMAL, enabled=True, desc="",
                  ctime=None):
        self.key_id = key_id
        self.secret = secret
        self.key_type = key_type
        self.username = username
        self.enabled = enabled
        self.desc = desc

        if ctime is None:
            self.ctime = datetime.datetime.now()
        else:
            self.ctime = ctime

    def __str__(self):
        return 'Key "{0}"'.format(self.key_id)

    def __json__(self):
        obj_dict = {}
        for k, v in self.__dict__.items():
            if not k.startswith('_'):
                obj_dict[k] = v
        obj_dict.pop("secret") #  no secret print
        return obj_dict


class AccessKeyManager(object):
    MAX_KEYS_PER_USER = 5

    def __init__(self, access_key_dao=None, user_dao=None, dao_context_mngr=None):
        self._user_dao = user_dao
        self._key_dao = access_key_dao
        self._dao_context_mngr =dao_context_mngr

    @staticmethod
    def _generate_base64_key(byte_number):
        if sys.version_info[:1] < (3, ):
            key_bytes = bytes(bytearray(random.getrandbits(8) for i in range(byte_number)))
        else:
            key_bytes = bytes(random.getrandbits(8) for i in range(byte_number))
        return base64.urlsafe_b64encode(key_bytes)

    def get_key_list_in_pages(self, key_type=None, username=None, start_index=0, max_number=65535):
        with self._dao_context_mngr.context():
            access_key_list = self._key_dao.get_list(
                key_type=key_type,
                username=username,
                start_index=start_index,
                max_number=max_number)
            access_key_total_count = self._key_dao.get_count(
                key_type=key_type,
                username=username)
        return access_key_total_count, access_key_list

    def get_access_key(self, key_id):
        with self._dao_context_mngr.context():
            access_key = self._key_dao.get_by_key_id(key_id)
            if access_key is None:
                raise IVRError("access_key Not Found", 404)
        return access_key

    def get_key_secret(self, key_id):
        with self._dao_context_mngr.context():
            access_key = self._key_dao.get_by_key_id(key_id)
            if access_key is None:
                raise IVRError("access_key Not Found", 404)
        return access_key.secret

    def new_access_key(self, username, **kwargs):
        key_id = self._generate_base64_key(15)  # 20 chars length
        secret = self._generate_base64_key(30)  # 40 chars length
        access_key = AccessKey(key_id=key_id, secret=secret, username=username,
                               **kwargs)
        with self._dao_context_mngr.context():
            user = self._user_dao.get_by_username(username)
            if user is None:
                raise IVRError("User Not Found", 404)
            if access_key.key_type == AccessKey.KEY_TYPE_PRIVILEGE and \
               (user.flags & User.USER_FLAG_PRIVILEGE) == 0:
                raise IVRError("key of KEY_TYPE_PRIVILEGE type cannot be created by user %s" % username,
                               400)
            access_key_list = self._key_dao.get_list(username=username)
            if len(access_key_list) >= self.MAX_KEYS_PER_USER:
                raise IVRError("%s access key is limited per user" % self.MAX_KEYS_PER_USER,
                               400)
            self._key_dao.add(access_key)
            access_key = self._key_dao.get_by_key_id(key_id)
        return access_key

    def del_access_key(self, key_id):
        with self._dao_context_mngr.context():
            access_key = self._key_dao.get_by_key_id(key_id)
            if access_key is None:
                raise IVRError("access_key Not Found", 404)
            self._key_dao.delete_by_key_id(key_id)

    def mod_access_key(self, key_id,  **kwargs):
        with self._dao_context_mngr.context():
            access_key = self._key_dao.get_by_key_id(key_id)
            if access_key is None:
                raise IVRError("access_key Not Found", 404)
            for (k, v) in kwargs.items():
                if k in ("enabled", "desc"):
                    setattr(access_key, k, v)
            self._key_dao.update(access_key)
        return access_key

