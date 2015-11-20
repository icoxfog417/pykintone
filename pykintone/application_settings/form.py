from pykintone.structure import FieldType
from pykintone.base_api import BaseAPI
import pykintone.application_settings.form_field as ff
import pykintone.application_settings.setting_result as sr


class FormAPI(BaseAPI):
    API_ROOT = "https://{0}.cybozu.com/k/v1{1}/app/form/fields.json"

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

        r = self._request("GET", url, params_or_data=params, use_api_token=False)
        return sr.GetFormResult(r)

    def add(self, json_or_models, app_id="", revision=-1):
        url = self._make_url(preview=True)
        body = self._format_fields(json_or_models, app_id if app_id else self.app_id, revision)

        r = self._request("POST", url, params_or_data=body, use_api_token=False)
        return sr.GetRevisionResult(r)

    def delete(self, json_or_models, app_id="", revision=-1):
        url = self._make_url(preview=True)
        codes = self._gather_codes(json_or_models)

        body = {
            "fields": codes
        }
        envelope = self.__pack(body, app_id, revision)

        r = self._request("DELETE", url, params_or_data=envelope, use_api_token=False)
        return sr.GetRevisionResult(r)

    @classmethod
    def _gather_codes(cls, fields):
        _fields = fields if isinstance(fields, (list, tuple)) else [fields]
        codes = []
        for f in _fields:
            c = ""
            if isinstance(f, ff.BaseField):
                c = f.code
            else:
                body = list(f.values())[0]
                c = "" if "code" not in body else body["code"]
            if c:
                codes.append(c)
        return codes

    def _format_fields(self, fields, app_id="", revision=-1):
        if "app" in fields and "properties" in fields:
            return fields

        def serialize(f): return f if not isinstance(f, ff.BaseField) else f.serialize()
        targets = fields if isinstance(fields, (list, tuple)) else [fields]

        properties = {}
        for t in targets:
            st = serialize(t)
            if "code" in st and "type" in st:
                properties[st["code"]] = st
            else:
                properties.update(st)

        formatted = {"properties": properties}
        envelope = self.__pack(formatted, app_id, revision)

        return envelope

    def __pack(self, pack, app_id="", revision=-1):
        _p = pack.copy()
        _p["app"] = app_id if app_id else self.app_id
        if revision > -1:
            _p["revision"] = revision

        return _p

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
