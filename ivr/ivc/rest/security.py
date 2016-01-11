# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division

from ivr.ivc.rest.common import get_view, post_view, put_view, delete_view
from ivr.ivc.rest.common import get_params_from_request
from ivr.common.schema import Schema, Optional, Default, IntVal, Use, BoolVal, StrVal, \
    StrRe, DoNotCare, STRING, AutoDel, EnumVal
from pyramid.response import Response
from zope.interface import implementer

from pyramid.interfaces import IAuthenticationPolicy
from pyramid.security import Authenticated, Everyone, DENY_ALL, Allow, Deny
from .common import get_token_from_request
import jwt
from ...common.exception import IVRError
from ..manager.user import User
import time


@implementer(IAuthenticationPolicy)
class IvcJwtAuthenticationPolicy(object):
    """ An object representing a JWT authentication policy for IVC. """

    def authenticated_userid(self, request):
        """ Return the authenticated :term:`userid` or ``None`` if
        no authenticated userid can be found. This method of the
        policy should ensure that a record exists in whatever
        persistent store is used related to the user (the user
        should not have been deleted); if a record associated with
        the current id does not exist in a persistent store, it
        should return ``None``.

        """
        options = {
            'verify_signature': False
        }
        jwt_str = get_token_from_request(request)
        if jwt_str is None:
            return None
        try:
            payload = jwt.decode(jwt_str, options=options)
            key_id = payload.get('iss')
            if key_id is None:
                raise IVRError('Token Invalid(iss absent)', 400)
            access_key = request.registry.access_key_mngr.get_access_key(key_id)
            payload = jwt.decode(jwt_str, access_key.secret, leeway=10)
        except jwt.exceptions.ExpiredSignatureError:
            raise IVRError('Token Expired', 400)
        except jwt.exceptions.InvalidTokenError:
            raise IVRError('Token Invalid', 400)
        username = payload.get('aud')
        if username is None:
            raise IVRError('Token Invalid(aud absent)', 400)
        if payload.get('exp') is None:
            raise IVRError('Token Invalid(exp absent)', 400)

        if access_key.username != username and \
           access_key.key_type != access_key.KEY_TYPE_PRIVILEGE:
            raise IVRError('Token Invalid(username mismatch)', 400)


        return username

    def unauthenticated_userid(self, request):
        """ Return the *unauthenticated* userid.  This method
        performs the same duty as ``authenticated_userid`` but is
        permitted to return the userid based only on data present
        in the request; it needn't (and shouldn't) check any
        persistent store to ensure that the user record related to
        the request userid exists.

        This method is intended primarily a helper to assist the
        ``authenticated_userid`` method in pulling credentials out
        of the request data, abstracting away the specific headers,
        query strings, etc that are used to authenticate the request.

        """
        options = {
            'verify_signature': False
        }
        jwt_str = get_token_from_request(request)
        if jwt_str is None:
            return None
        try:
            payload = jwt.decode(jwt_str, options=options)
            username = payload.get('aud')
            if username is None:
                raise IVRError('Token Invalid(aud absent)', 400)
        except jwt.exceptions.InvalidTokenError:
            raise IVRError('Token Invalid', 400)
        return username

    def effective_principals(self, request):
        """ Return a sequence representing the effective principals
        typically including the :term:`userid` and any groups belonged
        to by the current user, always including 'system' groups such
        as ``pyramid.security.Everyone`` and
        ``pyramid.security.Authenticated``.

        """
        principals = [Everyone]
        options = {
            'verify_signature': False
        }
        jwt_str = get_token_from_request(request)
        if jwt_str is None:
            return principals
        try:
            payload = jwt.decode(jwt_str, options=options)
            key_id = payload.get('iss')
            if key_id is None:
                raise IVRError('Token Invalid(iss absent)', 400)
            access_key = request.registry.access_key_mngr.get_access_key(key_id)
            payload = jwt.decode(jwt_str, access_key.secret, leeway=10)
        except jwt.exceptions.ExpiredSignatureError:
            raise IVRError('Token Expired', 400)
        except jwt.exceptions.InvalidTokenError:
            raise IVRError('Token Invalid', 400)

        username = payload.get('aud')
        user_type = payload.get('ust', User.USER_TYPE_NORMAL)
        if not username:
            raise IVRError('Token Invalid(aud absent)', 400)
        if payload.get('exp') is None:
            raise IVRError('Token Invalid(exp absent)', 400)
        if access_key.username != username and \
           access_key.key_type != access_key.KEY_TYPE_PRIVILEGE:
            raise IVRError('Token Invalid(aud mismatch)', 400)
        if user_type != User.USER_TYPE_NORMAL and \
            access_key.key_type != access_key.KEY_TYPE_PRIVILEGE:
            raise IVRError('Token Invalid(ust invalid)', 400)

        if username:
            principals += [Authenticated, username]
        if user_type == User.USER_TYPE_ADMIN:
            principals += ['user_type:admin']
        project_list = request.registry.user_mngr.get_user_projects(username)
        for project in project_list:
            principals += [project.name]
        return principals

    def remember(self, request, userid, **kw):
        """ Return a set of headers suitable for 'remembering' the
        :term:`userid` named ``userid`` when set in a response.  An
        individual authentication policy and its consumers can
        decide on the composition and meaning of **kw.

        """
        return []

    def forget(self, request):
        """ Return a set of headers suitable for 'forgetting' the
        current user on subsequent requests.

        """
        return []


class ProjectContext(object):
    def __init__(self, request):
        project_name = request.matchdict['project_name']
        self.__acl__ = [
            (Allow, 'project:%s' % project_name, 'view'),  # allow project's user to view
            (Allow, 'user_type:admin', ('view', 'edit')),  # allow admin user's to edit&view
        ]
        project = request.registry.project_mngr.get_project(project_name)
        if project.is_public:
            self.__acl__.append(
                (Allow, Everyone, 'view'), # if project is public, allow all to view
            )
        self.__acl__.append(DENY_ALL)


class UserContext(object):
    def __init__(self, request):
        username = request.matchdict['username']
        self.__acl__ = [
            (Allow, username, ('view', 'edit')),  # allow project's user to view & edit
            (Allow, 'user_type:admin', ('view', 'edit')),  # allow admin user's to view&edit
            DENY_ALL,
        ]


class AdminContext(object):
    def __init__(self, request):
        self.__acl__ = [
            (Allow, 'role:admin', ('view', 'edit')),  # only allow admin user's to view&edit
            DENY_ALL,
        ]


class AccessKeyContext(object):
    def __init__(self, request):
        key_id = request.matchdict['key_id']
        access_key = request.registry.access_key_mngr.get_access_key(key_id)
        self.__acl__ = [
            (Allow, access_key.username, ('view', 'edit')),  # allow access_key's user to view & edit
            (Allow, 'user_type:admin', ('view', 'edit')),  # allow admin user's to view&edit
            DENY_ALL,
        ]


def includeme(config):
    # block device list resource
    # GET:    block device list
    config.add_route('jwt_list', '/jwts')
    config.add_route('server_timestamp', '/server_timestamp')


new_jwt_schema = Schema({
    'iss': StrRe(r"^\S+$"),
    'secret': StrRe(r"^\S+$"),
    'aud': StrRe(r"^\w+$"),
    Optional('exp'): Default(IntVal(min=0), default=0),
    Optional('ust'): IntVal(values=[0, 1]),
    DoNotCare(Use(STRING)): object  # for all other key we don't care
})


@post_view(route_name='test_jwt_list')
def post_test_jwt_list(request):
    params = get_params_from_request(request, new_jwt_schema)
    if params['exp'] == 0:
        params['exp'] = int(time.time()) + 3600
    secret = params.pop('secret')
    jwt_str = jwt.encode(params, secret)

    return {'jwt':jwt_str}


@get_view(route_name='server_timestamp')
def get_server_timestamp(request):
    now = int(time.time())
    return {'now': now}