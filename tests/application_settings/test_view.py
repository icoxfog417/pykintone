import unittest
import tests.envs as envs
import pykintone
from pykintone.application_settings.administrator import Administrator
import pykintone.application_settings.form_field as ff
from pykintone.application_settings.form import FormAPI
from pykintone.application_settings.view import View


class TestView(unittest.TestCase):
    TEST_APP = None

    @classmethod
    def setUpClass(cls):
        account = pykintone.load(envs.FILE_PATH).account
        admin = Administrator(account)
        cls.TEST_APP = admin.create_application("test view edit")

        fields = cls._default_form()
        add_result = admin.form().add(fields, app_id=cls.TEST_APP.app_id)

    @classmethod
    def tearDownClass(cls):
        account = pykintone.load(envs.FILE_PATH).account
        admin = Administrator(account)
        rollbacked = admin.rollback_settings(cls.TEST_APP.app_id)
        cls.TEST_APP = None

    def test_get_view(self):
        app = pykintone.load(envs.FILE_PATH).app()
        vr = app.administration().view().get()
        self.assertTrue(vr.ok)
        views = vr.views()
        self.assertTrue(len(views) > 0)

    def test_update_views(self):
        ks = pykintone.load(envs.FILE_PATH)
        view_api = ks.app(self.TEST_APP.app_id).administration().view()

        view_name = "test_view"
        codes = FormAPI.gather_codes(self._default_form())
        views = View.create(view_name, codes[1:])

        # add views
        add_result = view_api.update(views)
        self.assertTrue(add_result.ok)
        v_def = view_api.get(preview=True).views()
        self.assertEqual(1, len(v_def))

        # update fields
        views = [View.create(view_name, codes), View.create("another_view", codes,  index=2)]
        update_result = view_api.update(views, revision=add_result.revision)
        self.assertTrue(update_result.ok)
        v_def = view_api.get(preview=True).views()
        self.assertEqual(2, len(v_def))
        original = [v for v in v_def if v.name == view_name][0]
        self.assertEqual(len(codes), len(original.fields))

    @classmethod
    def _default_form(cls):
        f1 = ff.BaseFormField.create("SINGLE_LINE_TEXT", "title", "title")
        f2 = ff.BaseFormField.create("DATE", "registered_date", "registered_date")
        f3 = ff.BaseFormField.create("NUMBER", "money", "money")

        fields = [f1, f2, f3]
        return fields
