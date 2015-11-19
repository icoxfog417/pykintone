from pykintone.structure import FieldType
from pykintone.base_api import BaseAPI
import pykintone.application_settings.form_field as ff
import pykintone.application_settings.setting_result as sr


class FormAPI(BaseAPI):
    API_ROOT = "https://{0}.cybozu.com/k/v1/{1}app/form/fields.json"

    def __init__(self, account, api_token="", requests_options=(), app_id=""):
        super(FormAPI, self).__init__(account, api_token, requests_options, app_id)

    def _make_url(self, preview=False):
        url = self.API_ROOT.format(self.account.domain, "" if not preview else "/preview")
        return url

    def get(self, app_id="", lang="default", preview=False):
        url = self._make_url(preview)
        params = {
            "app":  app_id if app_id else self.app_id,
            "lang": lang
        }

        r = self._request("GET", url, params_or_data=params)
        return sr.GetFormResult(r)

    @classmethod
    def serialize_fields(cls, fields):
        pass

    @classmethod
    def to_fields(cls, properties):
        fields = []
        for k in properties:
            p = properties[k]
            field_type = None
            field_name = p["type"].upper()
            candidates = [e for e in list(FieldType) if e.value == field_name]
            if len(candidates) > 0:
                field_type = candidates[0]

            if not field_type:
                pass
            elif field_type == FieldType.LABEL:
                fields.append(ff.Label.deserialize(p))
            else:
                fields.append(ff.BaseFormField.deserialize(p))

        return fields
