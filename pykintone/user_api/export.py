from pykintone.base_api import BaseAPI
import pykintone.user_api.user_api_result as ur


class Export(BaseAPI):

    def __init__(self, account, requests_options=()):
        super(Export, self).__init__(account=account, requests_options=requests_options)

    def get_users(self, ids=(), codes=(), offset=-1, size=0):
        url = "https://{0}.cybozu.com/v1/users.json".format(self.account.domain)

        params = {}
        if len(ids) > 0:
            params["ids"] = ids
        if len(codes) > 0:
            params["codes"] = codes
        if offset > -1:
            params["offset"] = offset
        if size > 0:
            params["size"] = size

        resp = self._request("GET", url, params_or_data=params)
        r = ur.GetUsersResult(resp)
        return r

    def get_user_organization_titles(self, code):
        url = "https://{0}.cybozu.com/v1/user/organizations.json".format(self.account.domain)

        params = {
            "code": code
        }

        resp = self._request("GET", url, params_or_data=params)
        r = ur.UserOrganizationTitlesResult(resp)
        return r

    def get_user_groups(self, code):
        url = "https://{0}.cybozu.com/v1/user/groups.json".format(self.account.domain)

        params = {
            "code": code
        }

        resp = self._request("GET", url, params_or_data=params)
        r = ur.GetUserGroupsResult(resp)
        return r
