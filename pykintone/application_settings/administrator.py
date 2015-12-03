import json
import requests
import pykintone.structure as ps
from pykintone.application_settings.base_administration_api import BaseAdministrationAPI
import pykintone.application_settings.setting_result as sr


class Administrator(BaseAdministrationAPI):

    def __init__(self, account, api_token="", requests_options=(), app_id=""):
        super(Administrator, self).__init__(account, api_token, requests_options, app_id)

    def __get_admin(self):
        return self

    def transaction(self):
        self._cached_changes = True
        return self

    def get_app_info(self, app_id=""):
        url = "https://{0}.cybozu.com/k/v1/app.json".format(self.account.domain)

        params = {
            "id": app_id if app_id else self.app_id
        }

        r = self._request("GET", url, params_or_data=params, use_api_token=False)
        return sr.GetApplicationInformationResult(r)

    def select_app_info(self, app_ids=(), codes=(), name="", space_ids=(), limit=-1, offset=-1):
        url = "https://{0}.cybozu.com/k/v1/apps.json".format(self.account.domain)
        params = {}

        def set_array_parameter(name, array):
            for i, a in enumerate(array):
                params[name + "[{0}]".format(i)] = a

        if len(app_ids) > 0:
            set_array_parameter("ids", app_ids)
        if len(codes) > 0:
            set_array_parameter("codes", codes)
        if name:
            params["name"] = name
        if len(space_ids) > 0:
            set_array_parameter("spaceIds", space_ids)
        if limit > 0:
            params["limit"] = limit
        if offset >= 0:
            params["offset"] = offset

        r = self._request("GET", url, params_or_data=params, use_api_token=False)
        return sr.GetApplicationInformationsResult(r)

    def create_application(self, name, space_id="", thread_id=""):
        # this api is preview
        url = "https://{0}.cybozu.com/k/v1/preview/app.json".format(self.account.domain)

        headers = self.account.to_header()  # you can not use api token when create the application.
        body = {
            "name": name
        }
        if space_id:
            body["space"] = space_id
        if thread_id:
            body["thread"] = thread_id

        r = requests.post(url, headers=headers, data=json.dumps(body), **self.requests_options)
        cr = sr.CreateApplicationResult(r)
        self.app_id = cr.app_id
        return cr

    def copy_application(self, app_name, original_app_id, space_id="", thread_id=""):
        general_settings = self.general_settings().get(original_app_id)
        form_fields = self.form().get(original_app_id)
        form_layout = self.form().get_layout(original_app_id)
        views = self.view().get(original_app_id)

        if general_settings.ok and form_fields.ok and form_layout.ok and views.ok:
            # begin create application
            created = self.create_application(app_name, space_id, thread_id)
            app_id = created.app_id

            def pack(j, wrap_key="", replaces=()):
                p = {}
                if isinstance(j, dict):
                    for k in j:
                        if len(replaces) > 0 and k in replaces:
                            p[k] = replaces[k]
                        else:
                            p[k] = j[k]
                else:
                    p = j
                if wrap_key:
                    p = {wrap_key: p}
                p["app"] = app_id
                return p

            def select_fields(j):
                from pykintone.account import kintoneService
                p = {}
                ignores = kintoneService.get_default_field_list(as_str=True)
                for k in j:
                    if "enabled" in j[k] and not j[k]["enabled"]:
                        continue
                    elif "type" in j[k] and j[k]["type"] in ignores:
                        continue
                    else:
                        p[k] = j[k]
                return p

            g_update = self.general_settings().update(pack(general_settings.raw, replaces={"name": app_name, "icon": None}))
            f_update = self.form().add(pack(select_fields(form_fields.raw), wrap_key="properties"))
            fl_update = self.form().update_layout(pack(form_layout.raw, "layout"))
            v_update = self.view().update(pack(views.raw, "views"))

            if g_update.ok and f_update.ok and fl_update.ok and v_update.ok:
                self._cached_changes = True
                return created
            else:
                failed_msg = []
                for n, r in [
                    ("General Settings", g_update),
                    ("Form Update", f_update),
                    ("Form Layout", fl_update),
                    ("View Update", v_update)]:

                    if not r.ok:
                        failed_msg += [n + ":" + r.error.message]
                raise Exception(
                    "Error is occurred when creating the the application. \n{0}".format("\n".join(failed_msg))
                )
        else:
            raise Exception("Error is occurred when getting the application settings.")

    def commit_settings(self, app_id, revision=-1):
        r = self.__deploy_application(app_id, revision)
        return r

    def rollback_settings(self, app_id, revision=-1):
        r = self.__deploy_application(app_id, revision, rollback=True)
        return r

    def __deploy_application(self, app_id, revision=-1, rollback=False):
        # this api is preview
        url = "https://{0}.cybozu.com/k/v1/preview/app/deploy.json".format(self.account.domain)

        def serialize(a, r):
            s = {"app": a}
            if r > -1:
                s["revision"] = r
            return s

        _app_id = app_id if app_id else self.app_id
        _revision = revision if revision > -1 else self._commit_revision
        headers = self.account.to_header()  # you can not use api token when create the application.
        body = {
            "apps": [serialize(_app_id, _revision)],
            "revert": rollback
        }

        r = requests.post(url, headers=headers, data=json.dumps(body), **self.requests_options)
        if r.ok:
            # wait till application deploy complete
            result = self.wait_until_complete([_app_id])
            return sr.DeployResult(r, result)
        else:
            return sr.DeployResult(r, None)

    def wait_until_complete(self, app_id_or_ids):
        from time import sleep
        processing = True
        wait_limit = 3
        interval = 0.5
        elapsed = 0
        result = {}

        apps = app_id_or_ids
        if not isinstance(app_id_or_ids, (list, tuple)):
            apps = [apps]

        while processing and elapsed < wait_limit:
            r = self.confirm_deploy_progress(app_id_or_ids)
            if not r:
                processing = False

            for p in r.progresses:
                if p.status == "SUCCESS":
                    result[p.app_id] = True
                if p.status in ["FAIL", "CANCEL"]:
                    result[p.app_id] = False

            if len(result) == len(apps):
                processing = False
            else:

                sleep(interval)
                elapsed += interval

        return result

    def confirm_deploy_progress(self, app_ids):
        # this api is preview
        url = "https://{0}.cybozu.com/k/v1/preview/app/deploy.json".format(self.account.domain)

        headers = self.account.to_header()  # you can not use api token when create the application.
        params = {
            "apps": app_ids
        }

        r = requests.get(url, headers=headers, data=json.dumps(params), **self.requests_options)
        return sr.DeployProgressResult(r)

    def general_settings(self):
        from pykintone.application_settings.general_settings import GeneralSettingsAPI
        return GeneralSettingsAPI(self.account, self.api_token, self.requests_options, self.app_id)

    def form(self):
        from pykintone.application_settings.form import FormAPI
        return FormAPI(self.account, self.api_token, self.requests_options, self.app_id)

    def view(self):
        from pykintone.application_settings.view import ViewAPI
        return ViewAPI(self.account, self.api_token, self.requests_options, self.app_id)


class ApplicationInformation(ps.kintoneStructure):

    def __init__(self):
        super(ApplicationInformation, self).__init__()
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

        self._pd("app_id", name_style_conversion=True, unsent=True)
        self._pd("space_id", name_style_conversion=True, unsent=True)
        self._pd("thread_id", name_style_conversion=True, unsent=True)
        self._pd("created_at", field_type=ps.FieldType.TIME_STAMP, name_style_conversion=True, unsent=True)
        self._pd("creator", ps.FieldType.CREATOR, unsent=True)
        self._pd("modified_at", field_type=ps.FieldType.TIME_STAMP, name_style_conversion=True, unsent=True)
        self._pd("modifier", ps.FieldType.MODIFIER, unsent=True)

    def __str__(self):
        return "{0}: {1}".format(self.app_id, self.name)
