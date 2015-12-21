# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division


class Stream(object):
    def __init__(self, project_id, camera_id, quality):
        self.project_id = project_id
        self.camera_id = camera_id
        self.quality = quality
        self.start = None
        self.end = None


class StreamDAO(object):
    def __init__(self):
        pass

    def get_stream(self, project_id, camera_id, quality):
        pass

    def add_stream(self, stream):
        pass

    def update_stream(self, stream):
        pass
