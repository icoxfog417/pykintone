import unittest
import tests.envs as envs
import pykintone


class TestGeneralSettings(unittest.TestCase):

    def test_get_general_settings(self):
        app = pykintone.load(envs.FILE_PATH).app()
        s = app.administration().general_settings().get().settings()
        self.assertTrue(s.app_id)
        self.assertTrue(s.created_at)
        self.assertTrue(s.creator)

    def test_update_general_settings(self):
        app = pykintone.load(envs.FILE_PATH).app()

        g = app.administration().general_settings()
        s = g.get().settings()
        s.description = "test edit description"
        result = g.update(s)
        self.assertTrue(result.revision)

