import unittest
from datetime import datetime
import tests.envs as envs
import pykintone
from pykintone.model import kintoneModel
from pykintone.model import FieldType


class TestAppModel(kintoneModel):

    def __init__(self):
        super().__init__()
        self.my_key = ""
        self.stringField = ""
        self.numberField = 0
        self.radio = ""
        self.checkbox = []
        self.dateField = datetime.now()
        self.time = datetime.now()
        self.datetimeField = datetime.now()
        self.user_select = None

        self._field_types["time"] = FieldType.TIME
        self._field_types["datetimeField"] = FieldType.DATETIME
        self._field_types["user_select"] = FieldType.USER_SELECT


class TestModel(unittest.TestCase):

    def test_model(self):
        app = pykintone.load(envs.FILE_PATH).app()

        # initialize model
        model = TestAppModel()
        model.my_key = "model_test"
        model.stringField = "model_test"
        model.numberField = 1
        model.radio = "radio1"
        model.checkbox = ["check2"]

        # create model
        result = app.create(model)
        self.assertTrue(result.ok)

        # get model
        created = app.get(result.record_id).model(TestAppModel)

        # update model
        created.stringField = "model_updated"
        app.update(created)
        updated = app.get(result.record_id).model(TestAppModel)
        self.assertEqual("model_updated", updated.stringField)

        # delete model
        app.delete(updated)
        deleted = app.get(result.record_id).model(TestAppModel)
        self.assertFalse(deleted)

    def test_models(self):
        app = pykintone.load(envs.FILE_PATH).app()
        keyword = "models_test"
        select_models = lambda : app.select("stringField = \"{0}\"".format(keyword)).models(TestAppModel)

        # initialize model
        ms = []
        for i in range(2):
            m = TestAppModel()
            m.my_key = "model_test_{0}".format(i)
            m.stringField = keyword
            m.numberField = i
            ms.append(m)

        # create model
        result = app.batch_create(ms)
        self.assertTrue(result.ok)

        # get model
        createds = select_models()

        # update model
        for i, m in enumerate(createds):
            m.numberField = i + 1
        app.batch_update(createds)

        updateds = select_models()
        for i, m in enumerate(createds):
            self.assertEqual(i + 1, m.numberField)

        # delete model
        app.delete(updateds)
        deleted = select_models()
        self.assertEqual(0, len(deleted))

