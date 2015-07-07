import yaml
import requests


class Account():

    def __init__(self, domain,
                 login_id="", login_password="",
                 basic_id="", basic_password=""):
        self.domain = domain
        self.login_id = login_id
        self.login_password = login_password
        self.basic_id = basic_id
        self.basic_password = basic_password

    @classmethod
    def load(cls, path):
        apps = None

        with open(path, "rb") as f:
            a_dict = yaml.load(f)
            apps = cls.loads(a_dict)

        return apps

    @classmethod
    def loads(cls, account_dict):
        account = None

        # create account
        args = {
            "domain": account_dict["domain"]
        }
        for k in ["login", "basic"]:
            if k in account_dict:
                args[k + "_id"] = account_dict[k]["id"]
                args[k + "_password"] = account_dict[k]["password"]

        account = Account(**args)

        # load kintone apps
        apps = []
        for name in account_dict["apps"]:
            _a = account_dict["apps"][name]
            token = "" if "token" not in _a else _a["token"]
            app = Application(account, int(_a["id"]), token, name)
            apps.append(app)

        return Kintone(apps)

    def __str__(self):
        infos = []
        infos.append("domain:\t {0}".format(self.domain))
        infos.append("login:\t {0} / {1}".format(self.login_id, self.login_password))
        infos.append("basic:\t {0} / {1}".format(self.basic_id, self.basic_password))

        return "\n".join(infos)


class Kintone():

    def __init__(self, apps):
        self.__apps = apps

    def __len__(self):
        return len(self.__apps)

    def app(self, app_id=-1):
        if app_id < 0:
            return self.__apps[0]
        else:
            a = [a for a in self.__apps if a.app_id == app_id]
            return a


class Application():
    API_ROOT = "https://{0}.cybozu.com/k/v1/{1}"

    def __init__(self, account, app_id, api_token="", app_name=""):
        self.account = account
        self.app_id = app_id
        self.api_token = api_token
        self.app_name = app_name
        self.requests_opstions = {}

    def __make_headers(self, body=True):
        # create header
        header = {}
        header["Host"] = "{0}.cybozu.com:443".format(self.account.domain)
        if body:
            header["Content-Type"] = "application/json"

        def encode(user_id, password):
            import base64
            return base64.b64encode("{0}:{1}".format(user_id, password))

        if self.account.basic_id:
            auth = encode(self.account.basic_id, self.account.basic_password)
            header["Authorization"] = "Basic {0}".format(auth)

        if self.api_token:
            header["X-Cybozu-API-Token"] = self.api_token
        elif self.account.login_id:
            auth = encode(self.account.login_id, self.account.login_password)
            header["X-Cybozu-Authorization"] = auth

        return header

    def record(self, record_id):
        url = self.API_ROOT.format(self.account.domain, "record.json")
        headers = self.__make_headers(body=False)
        params = {
            "app": self.app_id,
            "id": record_id
        }

        r = requests.get(url, headers=headers, params=params)
        content = r.json()
        return content

    def records(self, query="", fields=()):
        url = self.API_ROOT.format(self.account.domain, "records.json")

        headers = self.__make_headers(body=False)
        params = {
            "app": self.app_id
        }

        if query:
            params["query"] = query

        if len(fields) > 0:
            params["fields"] = fields

        r = requests.get(url, headers=headers, params=params)
        content = r.json()

        return content

    def __str__(self):
        info = str(self.account)
        info += "\napp:\n"
        info += "  id={0}, token={1}".format(self.app_id, self.api_token)
        return info
