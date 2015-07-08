import unittest
import tests.envs as envs
import pykintone
from pykintone import model


class TestAppModel(model.KintoneModel):

    def __init__(self):
        super().__init__()
        self.stringField = ""
        self.numberField = 0
        self.radio = ""
        self.checkbox = []


class TestModel(unittest.TestCase):

    def test_model(self):
        app = pykintone.load(envs.FILE_PATH).app()
        models = app.select().models(TestAppModel)
        self.assertTrue(len(models) > 0)
        self.assertTrue(models[0].stringField)
