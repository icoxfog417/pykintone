import pykintone.structure as ps
from pykintone.base_api import BaseAPI
import pykintone.application_settings.setting_result as sr


class GeneralSettingsAPI(BaseAPI):
    API_ROOT = "https://{0}.cybozu.com/k/v1/app.json"

    def __init__(self, account, api_token="", requests_options=(), app_id=""):
        super(GeneralSettingsAPI, self).__init__(account, api_token, requests_options, app_id)

    def get(self, app_id=""):
        url = self.API_ROOT.format(self.account.domain)
        _app_id = app_id if app_id else self.app_id

        params = {
            "id": _app_id
        }

        r = self._request("GET", url, params_or_data=params)
        return sr.SingleGeneralResult(r)

    def select(self, query):
        # todo: implements select applications
        pass

    def update(self, json_or_model):
        # update is preview feature.
        url = "https://{0}.cybozu.com/k/v1/preview/app/settings.json".format(self.account.domain)

        _body = json_or_model
        if isinstance(json_or_model, GeneralSettings):
            _body = json_or_model.serialize()
            _body["app"] = json_or_model.app_id

        r = self._request("PUT", url, params_or_data=_body, use_api_token=False)
        return sr.GetRevisionResult(r)


class GeneralSettings(ps.kintoneStructure):

    def __init__(self):
        super(GeneralSettings, self).__init__()
        self.app_id = ""
        # self.code = "" # nothing is set
        self.name = ""
        self.description = ""
        self.space_id = ""
        self.thread_id = ""
        self.created_at = None
        self.creator = None
        self.modified_at = None
        self.modifier = None

        self._property_details.append(ps.PropertyDetail("app_id", field_name="appId", unsent=True))
        self._property_details.append(ps.PropertyDetail("space_id", field_name="spaceId", unsent=True))
        self._property_details.append(ps.PropertyDetail("thread_id", field_name="threadId", unsent=True))
        self._property_details.append(ps.PropertyDetail("created_at", field_name="createdAt", field_type=ps.FieldType.TIME_STAMP, unsent=True))
        self._property_details.append(ps.PropertyDetail("creator", ps.FieldType.CREATOR, unsent=True))
        self._property_details.append(ps.PropertyDetail("modified_at", field_name="modifiedAt", field_type=ps.FieldType.TIME_STAMP, unsent=True))
        self._property_details.append(ps.PropertyDetail("modifier", ps.FieldType.MODIFIER, unsent=True))

    def serialize(self):
        return self._serialize(lambda name, value, pd: (name, value))

    @classmethod
    def deserialize(cls, json_body):
        return cls._deserialize(json_body, lambda f: (f, ""))

    def __str__(self):
        return "{0}: {1}".format(self.app_id, self.name)
