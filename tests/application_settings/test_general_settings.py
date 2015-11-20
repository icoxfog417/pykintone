import unittest
import tests.envs as envs
import pykintone
from pykintone.application_settings.administrator import Administrator


class TestGeneralSettings(unittest.TestCase):

    def test_get_general_settings(self):
        app = pykintone.load(envs.FILE_PATH).app()
        s = app.administration().general_settings().get().settings()
        self.assertTrue(s.app_id)
        self.assertTrue(s.created_at)
        self.assertTrue(s.creator)

    def test_update_general_settings(self):
        account = pykintone.load(envs.FILE_PATH).account
        admin = Administrator(account)

        created = admin.create_application("test_create_application")
        self.assertTrue(created.ok)
        rollbacked = admin.rollback_settings(created.app_id)
        self.assertTrue(rollbacked.ok)
        print(rollbacked.result)

        app = pykintone.load(envs.FILE_PATH).app()

        g = app.administration().general_settings()
        s = g.get().settings()
        s.description = "test edit description"
        result = g.update(s)
        self.assertTrue(result.revision)

