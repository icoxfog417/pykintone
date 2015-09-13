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
        result = app.get(record_id)
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
        result = app.create(record)
        self.assertTrue(result.ok)

        record_id = result.record_id
        first_revision = result.revision
        created = app.get(record_id)
        self.assertTrue(created.ok)

        # update
        update = {
            "$id": {
                "value": record_id
            },
            "$revision": {
                "value": result.revision
            },
            "radio": {
                "value": "radio2"
            }
        }
        result = app.update(update)
        self.assertTrue(result.ok)
        self.assertTrue(first_revision < result.revision)
        updated = app.get(record_id).record
        self.assertTrue("redio2", updated["radio"]["value"])

        # delete
        result = app.delete(record_id)
        self.assertTrue(result.ok)

    def test_batch(self):
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
        result = app.batch_create(records)
        self.assertTrue(result.ok)

        record_keys = result.keys
        ids = [str(k.record_id) for k in record_keys]
        query = "レコード番号 in ({0})".format(",".join(ids))
        created = app.select(query)
        self.assertTrue(created.ok)

        # update
        updates = [
            {
                "$id": {
                    "value": record_keys[0].record_id
                },
                "$revision": {
                    "value": record_keys[0].revision
                },
                "radio": {
                    "value": "radio2"
                }
            },
            {
                "$id": {
                    "value": record_keys[1].record_id
                },
                "$revision": {
                    "value": record_keys[1].revision
                },
                "radio": {
                    "value": "radio1"
                }
            }
        ]
        result = app.batch_update(updates)
        self.assertTrue(result.ok)
        for r in result.keys:
            prev = [k for k in record_keys if k.record_id == r.record_id]
            self.assertTrue(len(prev) == 1)
            self.assertTrue(prev[0].revision < r.revision)

        # delete
        result = app.delete(ids)
        self.assertTrue(result.ok)

    def test_error(self):
        app = pykintone.load(envs.FILE_PATH).app()

        record = {
            "radio": {
                "value": "xxxxx"
            }
        }

        # create (will be error)
        result = app.create(record)
        self.assertFalse(result.ok)

    def test_options(self):
        app = pykintone.load(envs.FILE_PATH).app()
        app.requests_opstions = {
            "verify": True
        }
        result = app.select()
        self.assertTrue(result.ok)
        self.assertTrue(len(result.records) > 0)
