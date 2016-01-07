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
        return self.unauthenticated_userid(request)

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
        return "abc"  # test user

    def effective_principals(self, request):
        """ Return a sequence representing the effective principals
        typically including the :term:`userid` and any groups belonged
        to by the current user, always including 'system' groups such
        as ``pyramid.security.Everyone`` and
        ``pyramid.security.Authenticated``.

        """
        principals = [Everyone]
        userid = self.authenticated_userid(request)
        if userid:
            principals += [Authenticated, str(userid)]
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
            (Allow, 'role:admin', ('view', 'edit')),  # allow admin user's to edit&view
        ]
        project = request.registry.project_mngr.get_project(project_name)
        if project.is_public != 0:
            self.__acl__.append(
                (Allow, Everyone, 'view'), # if project is public, allow all to view
            )
        self.__acl__.append(DENY_ALL)


class UserContext(object):
    def __init__(self, request):
        username = request.matchdict['username']
        self.__acl__ = [
            (Allow, username, ('view', 'edit')),  # allow project's user to view & edit
            (Allow, 'role:admin', ('view', 'edit')),  # allow admin user's to view&edit
            DENY_ALL,
        ]


class AdminContext(object):
    def __init__(self, request):
        self.__acl__ = [
            (Allow, 'role:admin', ('view', 'edit')),  # only allow admin user's to view&edit
            DENY_ALL,
        ]



