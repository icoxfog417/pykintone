import unittest
import tests.envs as envs
import pykintone


class TestForm(unittest.TestCase):

    def test_get_form(self):
        app = pykintone.load(envs.FILE_PATH).app()
        fr = app.administration().form().get()
        self.assertTrue(fr.ok)
        fields = fr.fields()
        self.assertTrue(len(fields) > 0)

