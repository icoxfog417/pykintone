import unittest
import tests.envs as envs
import pykintone
from pykintone.application_settings.administrator import Administrator


class TestGeneral(unittest.TestCase):

    def test_get_application_settings(self):
        app = pykintone.load(envs.FILE_PATH).app()
        s = app.administration().get_application().settings()
        self.assertTrue(s.app_id)

    def test_create_rollback_application(self):
        account = pykintone.load(envs.FILE_PATH).account

        with Administrator(account).as_test_mode() as admin:
            created = admin.create_application("test_create_application")
            admin.revision = created.revision
            self.assertTrue(created.ok)
