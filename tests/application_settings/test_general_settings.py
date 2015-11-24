import unittest
import tests.envs as envs
import pykintone
from pykintone.application_settings.administrator import Administrator


class TestGeneralSettings(unittest.TestCase):

    def test_get_general_settings(self):
        app = pykintone.load(envs.FILE_PATH).app()
        s = app.administration().general_settings().get().settings()
        self.assertTrue(s.name)

    def test_update_general_settings(self):
        account = pykintone.load(envs.FILE_PATH).account

        with Administrator(account).as_test_mode() as admin:
            created = admin.create_application("test_create_application")
            self.assertTrue(created.ok)

            g = admin.general_settings()
            s = g.get(preview=True).settings()
            s.description = "test edit description"
            result = g.update(s)
            self.assertTrue(result.revision)
            after_updated = g.get(preview=True).settings()
            self.assertEquals(s.description, after_updated.description)
