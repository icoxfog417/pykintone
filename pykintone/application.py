import requests
import json
from pykintone.account import kintoneService
import pykintone.result as pykr


class Application(object):
    API_ROOT = "https://{0}.cybozu.com/k/v1/{1}"

    def __init__(self, account, app_id, api_token="", app_name="", requests_options={}):
        self.account = account
        self.app_id = app_id
        self.api_token = api_token
        self.app_name = app_name
        self.requests_options = requests_options

    def __make_headers(self, body=True):
        # create header
        header = {}
        header["Host"] = "{0}.cybozu.com:443".format(self.account.domain)
        if body:
            header["Content-Type"] = "application/json"

        def encode(user_id, password):
            import base64
            return base64.b64encode("{0}:{1}".format(user_id, password).encode(kintoneService.ENCODE))

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

    def __is_record_id(self, field_name):
        return True if field_name in ["id", "$id"] else False

    def __is_revision(self, field_name):
        return True if field_name in ["revision", "$revision"] else False

    def get(self, record_id):
        url = self.__single()
        headers = self.__make_headers(body=False)
        params = {
            "app": self.app_id,
            "id": record_id
        }

        r = requests.get(url, headers=headers, params=params, **self.requests_options)
        return pykr.SelectSingleResult(r)

    def select(self, query="", fields=()):
        url = self.__multiple()

        headers = self.__make_headers()
        headers["X-HTTP-Method-Override"] = "GET"  # use post to get
        data = {
            "app": self.app_id,
            "totalCount": True
        }

        if query:
            data["query"] = query

        if len(fields) > 0:
            data["fields"] = fields

        r = requests.post(url, headers=headers, data=json.dumps(data), **self.requests_options)
        return pykr.SelectResult(r)

    def __get_model_type(self, instance):
        import pykintone.model as pykm
        if isinstance(instance, pykm.kintoneModel):
            return instance.__class__
        else:
            return None

    def __to_create_format(self, record_or_model):
        formatted = {}
        record = record_or_model
        if self.__get_model_type(record_or_model):
            record = record_or_model.to_record()

        for k in record:
            if self.__is_record_id(k) or self.__is_revision(k):
                continue
            else:
                formatted[k] = record[k]

        return formatted

    def create(self, record_or_model):
        url = self.__single()
        headers = self.__make_headers()
        _record = self.__to_create_format(record_or_model)

        data = {
            "app": self.app_id,
            "record": _record
        }

        resp = requests.post(url, headers=headers, data=json.dumps(data), **self.requests_options)
        r = pykr.CreateResult(resp)

        return r

    def batch_create(self, records_or_models):
        url = self.__multiple()
        headers = self.__make_headers()
        _records = [self.__to_create_format(r) for r in records_or_models]

        data = {
            "app": self.app_id,
            "records": _records
        }

        resp = requests.post(url, headers=headers, data=json.dumps(data), **self.requests_options)
        r = pykr.BatchCreateResult(resp)

        return r

    def __to_update_format(self, record_or_model):
        formatted = {"id": -1, "revision": -1, "record": {}}
        record = record_or_model
        if self.__get_model_type(record_or_model):
            record = record_or_model.to_record()

        for k in record:
            value = record[k]["value"]
            if self.__is_record_id(k) and value >= 0:
                formatted["id"] = value
            elif self.__is_revision(k) and value >= 0:
                formatted["revision"] = value
            else:
                formatted["record"][k] = record[k]

        return formatted

    def update(self, record_or_model):
        url = self.__single()
        headers = self.__make_headers()

        data = self.__to_update_format(record_or_model)
        data["app"] = self.app_id

        resp = requests.put(url, headers=headers, data=json.dumps(data), **self.requests_options)
        r = pykr.UpdateResult(resp)

        return r

    def batch_update(self, records_or_models):
        url = self.__multiple()
        headers = self.__make_headers()
        _records = [self.__to_update_format(r) for r in records_or_models]

        data = {
            "app": self.app_id,
            "records": _records
        }

        resp = requests.put(url, headers=headers, data=json.dumps(data), **self.requests_options)
        r = pykr.BatchUpdateResult(resp)

        return r

    def delete(self, record_ids_or_models, revisions=()):
        url = self.__multiple()
        headers = self.__make_headers()

        data = {
            "app": self.app_id,
            }

        ids = []
        revs = []

        if isinstance(revisions, (list, tuple)):
            if len(revisions) > 0:
                revs = [int(r) for r in revisions]
        else:
            revs = [int(revisions)]

        def to_key(id_or_m):
            if self.__get_model_type(id_or_m):
                return id_or_m.record_id, id_or_m.revision
            else:
                return int(id_or_m), -1

        def append_key(key):
            for i, k in enumerate(key):
                if k >= 0:
                    if i == 0:
                        ids.append(k)
                    else:
                        revs.append(k)

        if isinstance(record_ids_or_models, (list, tuple)):
            for i in record_ids_or_models:
                append_key(to_key(i))
        else:
            append_key(to_key(record_ids_or_models))

        if len(revs) > 0:
            if len(revs) != len(ids):
                raise Exception("when deleting, the size of ids have to be equal to revisions.")
            else:
                data["ids"] = ids
                data["revisions"] = revisions
        else:
            data["ids"] = ids

        resp = requests.delete(url, headers=headers, data=json.dumps(data), **self.requests_options)
        r = pykr.Result(resp)

        return r

    def __str__(self):
        info = str(self.account)
        info += "\napp:\n"
        info += "  id={0}, token={1}".format(self.app_id, self.api_token)
        return info
