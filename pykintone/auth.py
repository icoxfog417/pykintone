import os
import yaml


class kintoneAuth():

    def __init__(self, domain,
                 login_id="", login_password="",
                 basic_id="", basic_password="",
                 apps=()):
        self.domain = domain
        self.login_id = login_id
        self.login_password = login_password
        self.basic_id = basic_id
        self.basic_password = basic_password
        self.apps = {}
        if isinstance(apps, (list, tuple)):
            for a in apps:
                if isinstance(a, kintoneAppAuth):
                    self.apps[a.name] = a
        elif isinstance(apps, dict) and "app_id" in apps:
            _g = lambda k: "_" if k not in apps else apps[k]
            a = kintoneAppAuth(_g("name"), apps["app_id"], _g("api_token"))
            self.apps[a.name] = a

    @classmethod
    def load(cls, path):
        auth = None

        with open(path, "rb") as f:
            auth_dict = yaml.load(f)
            auth = cls.loads(auth_dict)

        return auth

    @classmethod
    def loads(cls, auth_dict):
        auth = None

        # prepare arguments to create kintone authorization object
        args = {
            "domain": auth_dict["domain"]
        }
        for k in ["login", "basic"]:
            if k in auth_dict:
                args[k + "_id"] = auth_dict[k]["id"]
                args[k + "_password"] = auth_dict[k]["password"]

        apps = []
        for name in auth_dict["apps"]:
            _auth = auth_dict["apps"][name]
            app = kintoneAppAuth(name, _auth["id"], "" if "token" not in _auth else _auth["token"])
            apps.append(app)

        args["apps"] = apps
        auth = kintoneAuth(**args)

        return auth

    def __str__(self):
        infos = []
        infos.append("domain:\t {0}".format(self.domain))
        infos.append("login:\t {0} / {1}".format(self.login_id, self.login_password))
        infos.append("basic:\t {0} / {1}".format(self.basic_id, self.basic_password))

        if len(self.apps.keys()) > 0:
            infos.append("apps:")
            for k in self.apps:
                infos.append("  " + str(self.apps[k]))

        return "\n".join(infos)

class kintoneAppAuth():

    def __init__(self, name, app_id, api_token=""):
        self.name = name
        self.app_id = app_id
        self.api_token = api_token

    def __str__(self):
        info = "{0}: id={1}, token={2}".format(self.name, self.app_id, self.api_token)
        return info
