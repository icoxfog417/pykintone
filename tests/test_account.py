import unittest
import tests.envs as envs
from pykintone.api import Account


class TestAccount(unittest.TestCase):

    def test_auth(self):
        account = Account("test_domain")
        self.assertTrue(account)
        print(account)

    def test_auth_load(self):
        apps = Account.load(envs.FILE_PATH)
        self.assertEqual(1, len(apps))
        print(apps.app())
