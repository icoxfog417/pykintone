import unittest
import tests.envs as envs
import pykintone
from pykintone.application_settings.administrator import Administrator
import pykintone.application_settings.form_field as ff
from pykintone.application_settings.view import View


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

    def test_create_application(self):
        account = pykintone.load(envs.FILE_PATH).account

        with Administrator(account).as_test_mode() as admin:
            # create application
            created = admin.create_application("my_application")

            # create form
            f1 = ff.BaseFormField.create("SINGLE_LINE_TEXT", "title", "Title")
            f2 = ff.BaseFormField.create("MULTI_LINE_TEXT", "description", "Desc")
            admin.form().add([f1, f2])

            # create view
            view = View.create("mylist", ["title", "description"])
            admin.view().update(view)
