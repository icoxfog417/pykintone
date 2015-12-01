from pykintone.base_api import BaseAPI


class BaseAdministrationAPI(BaseAPI):

    def __init__(self, account, api_token="", requests_options=(), app_id=""):
        super(BaseAdministrationAPI, self).__init__(account, api_token, requests_options, app_id)
        self.__test_mode = False
        self._commit_revision = -1
        self._cached_changes = False

    def as_test_mode(self):
        self.__test_mode = True
        return self

    def _request(self, method, url, params_or_data, headers=None, use_api_token=True):
        result = super(BaseAdministrationAPI, self)._request(method, url, params_or_data, headers, use_api_token)
        if method in ("POST", "PUT", "DELETE"):
            self._cached_changes = True
        return result

    def __enter__(self):
        self._commit_revision = -1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._cached_changes and not self.app_id:
            raise Exception("There are some changes to be committed, but no application id.")
        elif not (self._cached_changes and self.app_id):
            return None

        admin = self.__get_admin()
        result = None
        exit_type = "Commit"
        if exc_type is None and not self.__test_mode:
            result = admin.commit_settings(self.app_id, self._commit_revision)
        else:
            exit_type = "Rollback"
            result = admin.rollback_settings(self.app_id, self._commit_revision)

        if result.ok:
            self._commit_revision = -1
            self._cached_changes = False
        else:
            raise Exception(exit_type + " failed. {0}".format(result.message))

    def __get_admin(self):
        from pykintone.application_settings.administrator import Administrator
        admin = Administrator(self.account, self.api_token, self.requests_options, self.app_id)
        return admin
