import unittest
import tests.envs as envs
import pykintone
from pykintone import model


class TestAppModel(model.KintoneModel):

    def __init__(self):
        super().__init__()
        self.my_key = ""
        self.stringField = ""
        self.numberField = 0
        self.radio = ""
        self.checkbox = []


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
