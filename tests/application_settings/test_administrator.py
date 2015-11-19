import unittest
import tests.envs as envs
import pykintone
from pykintone.application_settings.administrator import Administrator


class TestGeneral(unittest.TestCase):

    def test_create_rollback_application(self):
        account = pykintone.load(envs.FILE_PATH).account
        admin = Administrator(account)

        created = admin.create_application("test_create_application")
        self.assertTrue(created.ok)
        rollbacked = admin.rollback_settings(created.app_id)
        self.assertTrue(rollbacked.ok)
        print(rollbacked.result)

