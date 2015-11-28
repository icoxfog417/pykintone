import unittest
import pykintone
import tests.envs as envs


class TestExport(unittest.TestCase):

    def test_uesrs(self):
        export_api = pykintone.load(envs.FILE_PATH).user_api().for_exporting
        users = export_api.get_users().users

        self.assertTrue(len(users) > 0)
        for u in users:
            self.assertTrue(u.name)

    def test_user_organization_titles(self):
        export_api = pykintone.load(envs.FILE_PATH).user_api().for_exporting
        users = export_api.get_users().users
        tested = False
        for u in users[:5]:
            code = u.code
            ots_result = export_api.get_user_organization_titles(code)
            self.assertTrue(ots_result.ok)

            ots = ots_result.organization_titles
            if len(ots) > 0:
                tested = True
                for ot in ots:
                    self.assertTrue(ot.organization.code)
                    self.assertTrue(ot.title.code)

        if not tested:
            print("Caution, organization and title deserialization is not checked. Please make user who belongs to some organization.")

    def test_uesr_groups(self):
        from datetime import datetime
        export_api = pykintone.load(envs.FILE_PATH).user_api().for_exporting
        users = export_api.get_users().users
        tested = False
        for u in users[:5]:
            code = u.code
            groups_result = export_api.get_user_groups(code)
            self.assertTrue(groups_result.ok)
            if len(groups_result.groups) > 0:
                tested = True
                for g in groups_result.groups:
                    self.assertTrue(g.name)

        if not tested:
            print("Caution, gruop deserialization is not checked. Please make user who belongs to some group.")
