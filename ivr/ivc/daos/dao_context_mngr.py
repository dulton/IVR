"""
ivr.ivc.daos.dao_context_mngr
~~~~~~~~~~~~~~~~~~~~~~~

This module defines the base class of DAO context manager

:copyright: (c) 2015 by OpenSight (www.opensight.cn).

"""

from __future__ import unicode_literals, division

CONTEXT_TYPE_TRANSACTION = 1
CONTEXT_TYPE_NESTED = 2

class DaoContext(object):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False


class DaoContextMngr(object):
    def context(self, context_type=CONTEXT_TYPE_TRANSACTION, **kwargs):
        pass