# -*- coding: utf-8 -*-
import unittest
import pykintone
from pykintone.model import kintoneModel
import tests.envs as envs


class TestAppModelSimple(kintoneModel):

    def __init__(self):
        super(TestAppModelSimple, self).__init__()
        self.my_key = ""
        self.stringField = ""


class TestComment(unittest.TestCase):

    def test_comment(self):
        app = pykintone.load(envs.FILE_PATH).app()

        model = TestAppModelSimple()
        model.my_key = "comment_test"
        model.stringField = "comment_test_now"

        result = app.create(model)
        self.assertTrue(result.ok)  # confirm create the record to test comment
        _record_id = result.record_id

        # create comment
        r_created = app.comment(_record_id).create("コメントのテスト")
        self.assertTrue(r_created.ok)
        # it requires Administrator user is registered in kintone
        r_created_m = app.comment(_record_id).create("メンションのテスト", [("Administrator", "USER")])
        self.assertTrue(r_created_m.ok)

        # select comment
        r_selected = app.comment(_record_id).select(True, 0, 10)
        self.assertTrue(r_selected.ok)
        self.assertTrue(2, len(r_selected.raw_comments))
        comments = r_selected.comments()
        self.assertTrue(1, len(comments[-1].mentions))

        # delete comment
        for c in comments:
            r_deleted = app.comment(_record_id).delete(c.comment_id)
            self.assertTrue(r_deleted.ok)
        r_selected = app.comment(_record_id).select()
        self.assertEqual(0, len(r_selected.raw_comments))

        # done test
        app.delete(_record_id)
