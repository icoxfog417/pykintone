import unittest
import tests.envs as envs
from pykintone.account import Account, kintoneService


class TestAccount(unittest.TestCase):

    def test_auth(self):
        account = Account("test_domain")
        self.assertTrue(account)
        print(account)

    def test_auth_load(self):
        apps = Account.load(envs.FILE_PATH)
        self.assertEqual(1, len(apps))
        print(apps.app())


class TestService(unittest.TestCase):

    def test_value_to_datetime(self):
        from datetime import datetime
        format = lambda d: d.strftime("%Y-%m-%d %H:%M:%S")
        utc = datetime.utcnow().strftime(kintoneService.DATETIME_FORMAT)
        local = format(datetime.now())

        localized = kintoneService.value_to_datetime(utc)
        self.assertEqual(local, format(localized))

    def test_datetime_to_value(self):
        from datetime import datetime
        import pytz
        utc = datetime.utcnow().replace(tzinfo=pytz.UTC).strftime(kintoneService.DATETIME_FORMAT)
        local = datetime.now()

        utced = kintoneService.datetime_to_value(local)
        self.assertEqual(utc, utced)
