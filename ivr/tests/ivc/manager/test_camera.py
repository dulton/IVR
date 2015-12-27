# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
import sys

if sys.version_info >= (2, 7):
    import unittest
else:
    import unittest2 as unittest

from ivr.ivc.manager.camera import Camera, CameraManager
from ivr.ivc.dummy_daos.camera import CameraDAO


class DummyDeviceManager(object):
    pass


class TestCameraMngr(unittest.TestCase):

    def setUp(self):
        self.camera_mngr = CameraManager(CameraDAO(), DummyDeviceManager())

    def tearDown(self):
        self.camera_mngr = None

    def test_add_delete_cameras(self):
        camera_list = [
            {
                'camera': Camera('p1', 'c1', device_uuid='d1', channel_index=0),
                'cameras_create': {'p1': ['c1'], 'p2': []},
                'cameras_delete': {'p1': ['c2', 'c4'], 'p2': ['c3']},
            },
            {
                'camera': Camera('p1', 'c2', device_uuid='d1', channel_index=1),
                'cameras_create': {'p1': ['c1', 'c2'], 'p2': []},
                'cameras_delete': {'p1': ['c4'], 'p2': ['c3']},
            },
            {
                'camera': Camera('p2', 'c3', device_uuid='d2', channel_index=0),
                'cameras_create': {'p1': ['c1', 'c2'], 'p2': ['c3']},
                'cameras_delete': {'p1': ['c4'], 'p2': []},
            },
            {
                'camera': Camera('p1', 'c4', device_uuid='d1', channel_index=2),
                'cameras_create': {'p1': ['c1', 'c2', 'c4'], 'p2': ['c3']},
                'cameras_delete': {'p1': [], 'p2': []},
            },
        ]
        # add cameras
        for data in camera_list:
            self.assertIsNone(self.camera_mngr.get_camera(data['camera'].project_name, data['camera'].uuid))
            self.camera_mngr.add_camera(data['camera'])
            for p, cs in data['cameras_create'].iteritems():
                self.assertEqual(self.camera_mngr.get_camera_count(p), len(cs))
                dao_cameras = self.camera_mngr.get_camera_list(p, start=0, limit=100)
                self.assertEqual(len(dao_cameras), len(cs))
                for dao_c in dao_cameras:
                    self.assertIn(dao_c.uuid, cs)
        # delete cameras
        for data in camera_list:
            self.camera_mngr.delete_camera(data['camera'].project_name, data['camera'])
            for p, cs in data['cameras_delete'].iteritems():
                self.assertEqual(self.camera_mngr.get_camera_count(p), len(cs))
                dao_cameras = self.camera_mngr.get_camera_list(p, start=0, limit=100)
                self.assertEqual(len(dao_cameras), len(cs))
                for dao_c in dao_cameras:
                    self.assertIn(dao_c.uuid, cs)

    def test_not_allow_get_camera_with_wrong_project(self):
        self.camera_mngr.add_camera(Camera('p1', 'c1', device_uuid='d1', channel_index=0))
        self.assertIsNone(self.camera_mngr.get_camera('p2', 'c1'))

    def test_not_allow_delete_camera_with_wrong_project(self):
        self.camera_mngr.add_camera(Camera('p1', 'c1', device_uuid='d1', channel_index=0))
        self.camera_mngr.delete_camera('p1', Camera('p2', 'c1', device_uuid='d1', channel_index=0))
        camera = self.camera_mngr.get_camera('p1', 'c1')
        self.assertIsNotNone(camera)
        self.assertEqual(camera.project_name, 'p1')
        self.assertEqual(camera.uuid, 'c1')


