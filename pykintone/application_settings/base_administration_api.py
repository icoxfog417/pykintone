from pykintone.base_api import BaseAPI


class BaseAdministrationAPI(BaseAPI):

    def __init__(self, account, api_token="", requests_options=(), app_id=""):
        super(BaseAdministrationAPI, self).__init__(account, api_token, requests_options, app_id)
        self.__test_mode = False
        self._commit_revision = -1

    def as_test_mode(self):
        self.__test_mode = True
        return self

    def __enter__(self):
        self._commit_revision = -1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self.app_id:
            raise Exception("Can not configure app_id.")

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
        else:
            raise Exception(exit_type + " failed. {0}".format(result.message))

    def __get_admin(self):
        from pykintone.application_settings.administrator import Administrator
        admin = Administrator(self.account, self.api_token, self.requests_options, self.app_id)
        return admin
