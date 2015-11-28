import pykintone.structure as ps
from pykintone.application_settings.base_administration_api import BaseAdministrationAPI
import pykintone.application_settings.setting_result as sr


class GeneralSettingsAPI(BaseAdministrationAPI):
    API_ROOT = "https://{0}.cybozu.com/k/v1{1}/app/settings.json"

    def __init__(self, account, api_token="", requests_options=(), app_id=""):
        super(GeneralSettingsAPI, self).__init__(account, api_token, requests_options, app_id)

    def _make_url(self, preview=False):
        url = self.API_ROOT.format(self.account.domain, "" if not preview else "/preview")
        return url

    def get(self, app_id="", lang="default", preview=False):
        url = self._make_url(preview)

        params = {
            "app": app_id if app_id else self.app_id,
            "lang": lang
        }

        r = self._request("GET", url, params_or_data=params, use_api_token=False)
        return sr.GetGeneralSettingsResult(r)

    def update(self, json_or_model, app_id="", revision=-1):
        # update is preview feature.
        url = self._make_url(preview=True)

        _body = json_or_model
        if isinstance(json_or_model, GeneralSettings):
            _body = json_or_model.serialize()

        _body["app"] = app_id if app_id else self.app_id
        if revision > -1:
            _body["revision"] = revision

        r = self._request("PUT", url, params_or_data=_body, use_api_token=False)
        return sr.GetRevisionResult(r)


class GeneralSettings(ps.kintoneStructure):

    def __init__(self):
        super(GeneralSettings, self).__init__()
        self.name = ""
        self.description = ""
        self.icon = None
        self.theme = ""
        self.revision = -1

    def __str__(self):
        return "{0}: {1}".format(self.name, self.description)
