# -*- coding: utf-8 -*-
import unittest
import tests.envs as envs
import pykintone


class TestApp(unittest.TestCase):

    def test_select(self):
        app = pykintone.load(envs.FILE_PATH).app()
        result = app.select()
        self.assertTrue(result.ok)
        self.assertTrue(len(result.records) > 0)

        record_id = result.records[0]["$id"]["value"]
        result = app.select_single(record_id)
        self.assertTrue(result.ok)
        print(result.record)

    def test_single(self):
        app = pykintone.load(envs.FILE_PATH).app()

        record = {
            "my_key": {
                "value": "test0"
            },
            "radio": {
                "value": "radio1"
            }
        }

        # create
        result = app.create_single(record)
        self.assertTrue(result.ok)

        record_id = result.key.record_id
        first_revision = result.key.revision
        created = app.select_single(record_id)
        self.assertTrue(created.ok)

        # update
        update_content = {
            "radio": {
                "value": "radio2"
            }
        }
        result = app.update_single(update_content, record_id, result.key.revision)
        self.assertTrue(result.ok)
        self.assertTrue(first_revision < result.revision)

        # delete
        result = app.delete(record_id)
        self.assertTrue(result.ok)

    def test_multiple(self):
        app = pykintone.load(envs.FILE_PATH).app()

        records = [
            {
                "my_key": {
                    "value": "test_m0"
                },
                "radio": {
                    "value": "radio1"
                }
            },
            {
                "my_key": {
                    "value": "test_m1"
                },
                "radio": {
                    "value": "radio2"
                }
            }
        ]

        # create
        result = app.create(records)
        self.assertTrue(result.ok)

        record_keys = result.keys
        ids = [str(k.record_id) for k in record_keys]
        query = "レコード番号 in ({0})".format(",".join(ids))
        created = app.select(query)
        self.assertTrue(created.ok)

        # update
        update_content = [
            {
                "id": record_keys[0].record_id,
                "revision": record_keys[0].revision,
                "radio": {
                    "value": "radio2"
                }
            },
            {
                "id": record_keys[1].record_id,
                "revision": record_keys[1].revision,
                "radio": {
                    "value": "radio1"
                }
            }
        ]
        result = app.update(update_content)
        self.assertTrue(result.ok)
        for r in result.keys:
            prev = [k for k in record_keys if k.record_id == r.record_id]
            self.assertTrue(len(prev) == 1)
            self.assertTrue(prev[0].revision < r.revision)

        # delete
        result = app.delete(ids)
        self.assertTrue(result.ok)
