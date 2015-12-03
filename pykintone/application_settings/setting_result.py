from collections import namedtuple
from pykintone.result import Result


class GetApplicationInformationResult(Result):

    def __init__(self, response):
        super(GetApplicationInformationResult, self).__init__(response)
        self.raw = {}
        self.info = None
        if self.ok:
            serialized = response.json()
            if "appId" in serialized:
                self.raw = serialized
                from pykintone.application_settings.administrator import ApplicationInformation
                self.info = ApplicationInformation.deserialize(self.raw)


class GetApplicationInformationsResult(Result):

    def __init__(self, response):
        super(GetApplicationInformationsResult, self).__init__(response)
        self.raw = {}
        self.infos = []
        if self.ok:
            serialized = response.json()
            if "apps" in serialized:
                self.raw = serialized["apps"]
                from pykintone.application_settings.administrator import ApplicationInformation
                self.infos = [ApplicationInformation.deserialize(a) for a in self.raw]


class GetGeneralSettingsResult(Result):

    def __init__(self, response):
        super(GetGeneralSettingsResult, self).__init__(response)
        self.raw = {}
        self.revision = -1
        self.settings = []
        if self.ok:
            serialized = response.json()
            if "revision" in serialized:
                self.revision = int(serialized["revision"])
                serialized.pop("revision")
                self.raw = serialized
                from pykintone.application_settings.general_settings import GeneralSettings
                self.settings = GeneralSettings.deserialize(self.raw)


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
        self.raw = {}
        self.revision = -1
        self.fields = []
        if self.ok:
            serialized = response.json()
            if "properties" in serialized:
                self.revision = int(serialized["revision"])
                self.raw = serialized["properties"]
                from pykintone.application_settings.form import FormAPI
                self.fields = FormAPI.load_properties(self.raw)


class GetLayoutResult(Result):

    def __init__(self, response):
        super(GetLayoutResult, self).__init__(response)
        self.raw = {}
        self.revision = -1
        self.layouts = []
        if self.ok:
            serialized = response.json()
            if "layout" in serialized:
                self.revision = int(serialized["revision"])
                self.raw = serialized["layout"]
                from pykintone.application_settings.form_layout import Layout
                self.layouts = [Layout.deserialize(ly) for ly in self.raw]


class GetViewResult(Result):

    def __init__(self, response):
        super(GetViewResult, self).__init__(response)
        self.raw = {}
        self.revision = -1
        self.views = []
        if self.ok:
            serialized = response.json()
            if "views" in serialized:
                self.revision = int(serialized["revision"])
                self.raw = serialized["views"]
                from pykintone.application_settings.view import View
                for k in self.raw:
                    v = View.deserialize(self.raw[k])
                    self.views.append(v)


class UpdateViewsResult(Result):

    def __init__(self, response):
        super(UpdateViewsResult, self).__init__(response)
        self.view_dict = {}
        self.revision = -1
        if self.ok:
            serialized = response.json()
            if "views" in serialized:
                self.revision = int(serialized["revision"])
                for k in serialized["views"]:
                    self.view_dict[k] = serialized["views"][k]["id"]
