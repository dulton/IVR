# -*- coding: utf-8 -*-


class IVRError(Exception):
    def __init__(self, msg, http_status_code=505):
        super(IVRError, self).__init__(msg)
        self.http_status_code = http_status_code

