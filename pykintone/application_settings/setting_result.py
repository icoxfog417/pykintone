from collections import namedtuple
from pykintone.result import Result


class SingleGeneralResult(Result):

    def __init__(self, response):
        super(SingleGeneralResult, self).__init__(response)
        self.value = {}
        if self.ok:
            serialized = response.json()
            if "appId" in serialized:
                self.value = serialized

    def settings(self):
        from pykintone.application_settings.general_settings import GeneralSettings
        return GeneralSettings.deserialize(self.value)


class GetRevisionResult(Result):

    def __init__(self, response):
        super(GetRevisionResult, self).__init__(response)
        self.revision = -1
        if self.ok:
            serialized = response.json()
            if "revision" in serialized:
                self.revision = int(serialized["revision"])


class CreateApplicationResult(Result):

    def __init__(self, response):
        super(CreateApplicationResult, self).__init__(response)
        self.app_id = -1
        self.revision = -1
        if self.ok:
            serialized = response.json()
            if "app" in serialized:
                self.app_id = int(serialized["app"])
                self.revision = int(serialized["revision"])


class DeployProgressResult(Result):

    def __init__(self, response):
        super(DeployProgressResult, self).__init__(response)
        Progress = namedtuple("Progress", ["app_id", "status"])
        self.progresses = []
        if self.ok:
            serialized = response.json()
            if "apps" in serialized:
                for a in serialized["apps"]:
                    p = Progress(a["app"], a["status"])
                    self.progresses.append(p)


class DeployResult(Result):

    def __init__(self, response, result):
        super(DeployResult, self).__init__(response)
        self.result = result


class GetFormResult(Result):

    def __init__(self, response):
        super(GetFormResult, self).__init__(response)
        self.properties = {}
        self.revision = -1
        if self.ok:
            serialized = response.json()
            if "properties" in serialized:
                self.revision = int(serialized["revision"])
                self.properties = serialized["properties"]

    def fields(self):
        from pykintone.application_settings.form import FormAPI
        return FormAPI.load_properties(self.properties)


class GetViewResult(Result):

    def __init__(self, response):
        super(GetViewResult, self).__init__(response)
        self.value = {}
        self.revision = -1
        if self.ok:
            serialized = response.json()
            if "views" in serialized:
                self.revision = int(serialized["revision"])
                self.value = serialized["views"]

    def views(self):
        from pykintone.application_settings.view import View
        views = []
        for k in self.value:
            v = View.deserialize(self.value[k])
            views.append(v)
        return views


class UpdateViewsResult(Result):

    def __init__(self, response):
        super(UpdateViewsResult, self).__init__(response)
        self.views = {}
        self.revision = -1
        if self.ok:
            serialized = response.json()
            if "views" in serialized:
                self.revision = int(serialized["revision"])
                for k in serialized["views"]:
                    self.views[k] = serialized["views"][k]["id"]
