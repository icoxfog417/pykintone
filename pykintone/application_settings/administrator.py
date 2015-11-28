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

    def get_application(self, app_id=""):
        url = "https://{0}.cybozu.com/k/v1/app.json".format(self.account.domain)

        params = {
            "id": app_id if app_id else self.app_id
        }

        r = self._request("GET", url, params_or_data=params, use_api_token=False)
        return sr.GetApplicationSettingsResult(r)

    def select_applications(self, app_ids=(), codes=(), name="", spaceIds=(), limit=-1, offset=-1):
        # todo: implements select applications
        pass

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


class ApplicationSettings(ps.kintoneStructure):

    def __init__(self):
        super(ApplicationSettings, self).__init__()
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
