import yaml
import requests
import json
import pykintone.result as result


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
        kintone = Kintone(account)

        # load kintone apps
        apps = []
        for name in account_dict["apps"]:
            _a = account_dict["apps"][name]
            token = "" if "token" not in _a else _a["token"]
            kintone.app(int(_a["id"]), token, name)

        return kintone

    def __str__(self):
        infos = []
        infos.append("domain:\t {0}".format(self.domain))
        infos.append("login:\t {0} / {1}".format(self.login_id, self.login_password))
        infos.append("basic:\t {0} / {1}".format(self.basic_id, self.basic_password))

        return "\n".join(infos)


class Kintone():
    ENCODE = "utf-8"

    def __init__(self, account):
        self.account = account
        self.__apps = []

    def __len__(self):
        return len(self.__apps)

    def app(self, app_id=-1, api_token="", app_name=""):
        if app_id < 0:
            return self.__apps[0]
        else:
            existed = [a for a in self.__apps if a.app_id == app_id]
            # register if not exist
            if len(existed) > 0:
                return existed[0]
            else:
                _a = Application(self.account, app_id, api_token, app_name)
                self.__apps.append(_a)
                return _a


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
            return base64.b64encode("{0}:{1}".format(user_id, password).encode(Kintone.ENCODE))

        if self.account.basic_id:
            auth = encode(self.account.basic_id, self.account.basic_password)
            header["Authorization"] = "Basic {0}".format(auth)

        if self.api_token:
            header["X-Cybozu-API-Token"] = self.api_token
        elif self.account.login_id:
            auth = encode(self.account.login_id, self.account.login_password)
            header["X-Cybozu-Authorization"] = auth

        return header

    def __single(self):
        return self.API_ROOT.format(self.account.domain, "record.json")

    def __multiple(self):
        return self.API_ROOT.format(self.account.domain, "records.json")

    def select_single(self, record_id):
        url = self.__single()
        headers = self.__make_headers(body=False)
        params = {
            "app": self.app_id,
            "id": record_id
        }

        r = requests.get(url, headers=headers, params=params)
        return result.SelectSingleResult(r)

    def select(self, query="", fields=()):
        url = self.__multiple()

        headers = self.__make_headers(body=False)
        params = {
            "app": self.app_id
        }

        if query:
            params["query"] = query

        if len(fields) > 0:
            params["fields"] = fields

        r = requests.get(url, headers=headers, params=params)
        return result.SelectResult(r)

    def create_single(self, record):
        url = self.__single()
        headers = self.__make_headers()

        data = {
            "app": self.app_id,
            "record": record
        }

        resp = requests.post(url, headers=headers, data=json.dumps(data))
        r = result.CreateSingleResult(resp)

        return r

    def create(self, records):
        url = self.__multiple()
        headers = self.__make_headers()

        data = {
            "app": self.app_id,
            "records": records
        }

        resp = requests.post(url, headers=headers, data=json.dumps(data))
        r = result.CreateResult(resp)

        return r

    def update_single(self, record, record_id, revision=-1):
        url = self.__single()
        headers = self.__make_headers()

        data = {
            "app": self.app_id,
            "id": record_id,
            "record": record
        }

        if revision > 0:
            data["revision"] = revision

        resp = requests.put(url, headers=headers, data=json.dumps(data))
        r = result.UpdateSingleResult(resp)

        return r

    def update(self, records):
        url = self.__multiple()
        headers = self.__make_headers()
        _records = []

        for r in records:
            r_id = -1
            r_rv = -1
            r_dict = {}

            for k in r:
                if k == "id" or k == "$id":
                    r_id = r[k]
                elif k == "revision" or k == "$revision":
                    r_rv = r[k]
                else:
                    r_dict[k] = r[k]

            _records.append({
                "id": r_id,
                "revision": r_rv,
                "record": r_dict
            })

        data = {
            "app": self.app_id,
            "records": _records
        }

        resp = requests.put(url, headers=headers, data=json.dumps(data))
        r = result.UpdateResult(resp)

        return r

    def delete(self, record_ids, revisions=()):
        url = self.__multiple()
        headers = self.__make_headers()
        ids = record_ids
        if not isinstance(ids, (list, tuple)):
            ids = [record_ids]

        data = {
            "app": self.app_id,
            "ids": ids
        }

        if len(revisions) > 0:
            if len(revisions) != len(record_ids):
                raise Exception("when deleting, the size of ids have to be equal to revisions.")
            data["revisions"] = revisions

        resp = requests.delete(url, headers=headers, data=json.dumps(data))
        r = result.Result(resp)

        return r

    def __str__(self):
        info = str(self.account)
        info += "\napp:\n"
        info += "  id={0}, token={1}".format(self.app_id, self.api_token)
        return info
