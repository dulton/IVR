# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division


class Stream(object):
    def __init__(self, project_id, camera_id, quality, stream_id, url):
        self.project_id = project_id
        self.camera_id = camera_id
        self.quality = quality
        self.stream_id = stream_id
        self.url = url
        self.start = None
        self.end = None


class StreamDAO(object):
    def __init__(self):
        pass

    def get_stream_list(self, project_id, camera_id):
        pass

    def get_stream(self, stream_id):
        pass

    def add_stream(self, stream):
        pass

    def update_stream(self, stream):
        pass

    def delete_stream(self, stream_id):
        pass