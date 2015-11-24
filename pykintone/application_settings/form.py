from pykintone.structure import FieldType
from pykintone.application_settings.base_administration_api import BaseAdministrationAPI
import pykintone.application_settings.form_field as ff
from pykintone.application_settings.form_layout import Layout
import pykintone.application_settings.setting_result as sr


class FormAPI(BaseAdministrationAPI):
    API_ROOT = "https://{0}.cybozu.com/k/v1{1}/app/form/{2}"

    def __init__(self, account, api_token="", requests_options=(), app_id=""):
        super(FormAPI, self).__init__(account, api_token, requests_options, app_id)

    def _make_url(self, preview=False, layout=False):
        kind = "fields.json"
        if layout:
            kind = "layout.json"

        url = self.API_ROOT.format(self.account.domain, "" if not preview else "/preview", kind)
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
        codes = self.gather_codes(json_or_models)

        body = {
            "fields": codes
        }
        envelope = self.__pack(body, app_id, revision)

        r = self._request("DELETE", url, params_or_data=envelope, use_api_token=False)
        return sr.GetRevisionResult(r)

    def get_layout(self, app_id="", preview=False):
        url = self._make_url(preview, layout=True)
        params = {
            "app":  app_id if app_id else self.app_id
        }

        r = self._request("GET", url, params_or_data=params, use_api_token=False)
        return sr.GetLayoutResult(r)

    def update_layout(self, json_or_layouts, app_id="", revision=-1):
        url = self._make_url(preview=True, layout=True)

        body = json_or_layouts
        if isinstance(json_or_layouts, dict) and "app" in json_or_layouts:
            pass
        else:
            targets = json_or_layouts if isinstance(json_or_layouts, (list, tuple)) else [json_or_layouts]
            def serialize(ly): return ly if not isinstance(ly, Layout) else ly.serialize()
            targets = [serialize(t) for t in targets]
            body = self.__pack({
                "layout": targets
            }, app_id, revision)

        r = self._request("PUT", url, params_or_data=body, use_api_token=False)
        return sr.GetRevisionResult(r)

    @classmethod
    def gather_codes(cls, fields):
        _fields = fields if isinstance(fields, (list, tuple)) else [fields]
        codes = []
        for f in _fields:
            c = ""
            if isinstance(f, ff.BaseField):
                c = f.code
            elif isinstance(f, dict) and "code" in f:
                c = f["code"]
            else:
                c = str(f)
            if c:
                codes.append(c)
        return codes

    def _format_fields(self, fields, app_id="", revision=-1):
        if isinstance(fields, dict) and ("app" in fields and "properties" in fields):
            return fields

        def serialize(f): return f if not isinstance(f, ff.BaseField) else f.serialize()
        targets = fields if isinstance(fields, (list, tuple)) else [fields]

        properties = {}
        for t in targets:
            st = serialize(t)
            if "code" in st and "type" in st:
                properties[st["code"]] = st

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
    def load_properties(cls, properties):
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
