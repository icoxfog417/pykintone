import pykintone.structure as ps
from pykintone.application_settings.base_administration_api import BaseAdministrationAPI
import pykintone.application_settings.setting_result as sr


class ViewAPI(BaseAdministrationAPI):
    API_ROOT = "https://{0}.cybozu.com/k/v1{1}/app/views.json"

    def __init__(self, account, api_token="", requests_options=(), app_id=""):
        super(ViewAPI, self).__init__(account, api_token, requests_options, app_id)

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
        return sr.GetViewResult(r)

    def update(self, json_or_views, app_id="", revision=-1):
        url = self._make_url(preview=True)

        body = self._format_views(json_or_views, app_id if app_id else self.app_id, revision)

        r = self._request("PUT", url, params_or_data=body, use_api_token=False)
        return sr.UpdateViewsResult(r)

    def _format_views(self, json_or_views, app_id="", revision=-1):
        if isinstance(json_or_views, dict) and ("app" in json_or_views and "views" in json_or_views):
            return json_or_views

        targets = json_or_views if isinstance(json_or_views, (list, tuple)) else [json_or_views]
        def serialize(v): return v if not isinstance(v, View) else v.serialize()

        views = {}
        for t in targets:
            st = serialize(t)
            if "name" in st and "type" in st:
                views[st["name"]] = st

        formatted = {
            "views": views
        }
        envelope = self.__pack(formatted, app_id, revision)
        return envelope

    def __pack(self, pack, app_id="", revision=-1):
        _p = pack.copy()
        _p["app"] = app_id if app_id else self.app_id
        if revision > -1:
            _p["revision"] = revision

        return _p


class View(ps.kintoneStructure):

    def __init__(self):
        super(View, self).__init__()
        self.name = ""
        self.view_id = ""
        self.view_type = "LIST"
        self.builtin_type = ""
        self.fields = []
        self.filter_cond = ""
        self.sort = ""
        self.index = 0

        self._pd("view_id", field_name="id")
        self._pd("view_type", field_name="type")
        self._pd("builtin_type", name_style_conversion=True)
        self._pd("filter_cond", name_style_conversion=True)

    @classmethod
    def create(cls, name, fields, view_type="", builtin_type="", filter_cond="", sort="", index=-1):
        from pykintone.application_settings.form import FormAPI
        v = View()
        v.name = name
        v.fields = FormAPI.gather_codes(fields)
        v.view_type = view_type if view_type else v.view_type
        v.builtin_type = builtin_type if builtin_type else v.builtin_type
        v.filter_cond = filter_cond
        v.sort = sort
        v.index = index if index > -1 else v.index
        return v

    def __str__(self):
        return "{0}: {1}".format(self.view_id, self.name)
