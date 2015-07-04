import os
import unittest
import pykintone.auth as auth


class TestAuth(unittest.TestCase):
    FILE_PATH = os.path.join(os.path.dirname(__file__), "../kintone.yaml")

    def test_auth(self):
        _auth = auth.kintoneAuth("dddd", apps={"name": "test", "app_id": 1})
        self.assertTrue(_auth.domain)
        self.assertTrue(_auth.apps["test"])
        print(_auth)

    def test_auth_load(self):
        _auth = auth.kintoneAuth.load(self.FILE_PATH)
        self.assertTrue(_auth.domain)
        print(_auth)
