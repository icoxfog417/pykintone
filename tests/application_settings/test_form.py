import unittest
import tests.envs as envs
import pykintone
from pykintone.application_settings.administrator import Administrator
import pykintone.application_settings.form_field as ff


class TestForm(unittest.TestCase):
    TEST_APP = None

    @classmethod
    def setUpClass(cls):
        account = pykintone.load(envs.FILE_PATH).account
        admin = Administrator(account)
        cls.TEST_APP = admin.create_application("test form edit")

    @classmethod
    def tearDownClass(cls):
        account = pykintone.load(envs.FILE_PATH).account
        admin = Administrator(account)
        rollbacked = admin.rollback_settings(cls.TEST_APP.app_id)
        cls.TEST_APP = None

    def test_get_form(self):
        app = pykintone.load(envs.FILE_PATH).app()
        fr = app.administration().form().get()
        self.assertTrue(fr.ok)
        fields = fr.fields()
        self.assertTrue(len(fields) > 0)

    def test_update_fields(self):
        ks = pykintone.load(envs.FILE_PATH)
        form_api = ks.app(self.TEST_APP.app_id).administration().form()

        fields = self._make_fields()
        codes = form_api.gather_codes(fields)

        def filter_by_codes(fs, target_codes):
            return [f for f in fs if f.code in target_codes]

        # add fields
        add_result = form_api.add(fields)
        self.assertTrue(add_result.ok)
        f_def = form_api.get(preview=True).fields()
        created = filter_by_codes(f_def, codes)
        self.assertEqual(len(fields), len(created))

        # delete fields
        delete_result = form_api.delete(fields, revision=add_result.revision)
        self.assertTrue(delete_result.ok)
        f_def = form_api.get(preview=True).fields()
        deleted = filter_by_codes(f_def, codes)
        self.assertEqual(0, len(deleted))

    def _make_fields(self):
        f1 = ff.BaseFormField.create("SINGLE_LINE_TEXT", "title", "title")
        f2 = {
                "code": "description",
                "type": "RICH_TEXT",
                "label": "Description",
                "defaultValue": "rich rich"
            }

        fields = [f1, f2]
        return fields
