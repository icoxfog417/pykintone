import json
import asyncio
import requests
from pykintone.base_api import BaseAPI
import pykintone.application_settings.setting_result as ar


class Administrator(BaseAPI):

    def __init__(self, account, api_token="", requests_options=(), app_id=""):
        super(Administrator, self).__init__(account, api_token, requests_options, app_id)

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
        return ar.CreateApplicationResult(r)

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

        headers = self.account.to_header()  # you can not use api token when create the application.
        body = {
            "apps": [serialize(app_id, revision)],
            "revert": rollback
        }

        r = requests.post(url, headers=headers, data=json.dumps(body), **self.requests_options)
        if r.ok:
            # wait till application deploy complete
            loop = asyncio.get_event_loop()
            result = loop.run_until_complete(self.wait_untill_complete([app_id]))
            return ar.DeployResult(r, result)
        else:
            return ar.DeployResult(r, None)

    @asyncio.coroutine
    def wait_untill_complete(self, app_id_or_ids):
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
                yield from asyncio.sleep(interval)
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
        return ar.DeployProgressResult(r)

    def general_settings(self):
        from pykintone.application_settings.general_settings import GeneralSettingsAPI
        return GeneralSettingsAPI(self.account, self.api_token, self.requests_options, self.app_id)

    def form(self):
        from pykintone.application_settings.form import FormAPI
        return FormAPI(self.account, self.api_token, self.requests_options, self.app_id)

    def view(self):
        from pykintone.application_settings.view import ViewAPI
        return ViewAPI(self.account, self.api_token, self.requests_options, self.app_id)
