# -*- coding: utf-8 -*-
import unittest
import tests.envs as envs
import pykintone


class TestPykintone(unittest.TestCase):

    def test_api_interface(self):
        # load from file
        kintone = pykintone.load(envs.FILE_PATH)
        app = kintone.app()
        self.assertTrue(app)

        # login
        app = pykintone.login("domain", "user_id", "password").app(1, api_token="token")
        self.assertTrue(app)

        # app
        app = pykintone.app("domain", 1, "token")
        self.assertTrue(app)
