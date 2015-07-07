import unittest
import envs
import pykintone


class TestApp(unittest.TestCase):

    def test_records(self):
        app = pykintone.load(envs.FILE_PATH).app()
        records = app.records()
        self.assertTrue("records" in records and len(records["records"]) > 0)

        record_id = records["records"][0]["$id"]["value"]
        record = app.record(record_id)
        self.assertTrue("record" in record)
        print(record)
