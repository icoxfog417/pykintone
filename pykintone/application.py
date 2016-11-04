from pykintone.base_api import BaseAPI
import pykintone.model_result as mr


class Application(BaseAPI):
    API_ROOT = "https://{0}.cybozu.com/k/v1/{1}"

    def __init__(self, account, app_id, api_token="", app_name="", requests_options=()):
        super(Application, self).__init__(account, api_token, requests_options, app_id)
        self.app_name = app_name

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
        params = {
            "app": self.app_id,
            "id": record_id
        }

        r = self._request("GET", url, params_or_data=params)
        return mr.SelectSingleResult(r)

    def select(self, query="", fields=()):
        url = self.__multiple()

        headers = self.account.to_header(self.api_token)
        headers["X-HTTP-Method-Override"] = "GET"  # use post to get
        data = {
            "app": self.app_id,
            "totalCount": True
        }

        if query:
            data["query"] = query

        if len(fields) > 0:
            data["fields"] = fields

        r = self._request("POST", url, headers=headers, params_or_data=data)
        return mr.SelectResult(r)

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
        _record = self.__to_create_format(record_or_model)

        data = {
            "app": self.app_id,
            "record": _record
        }

        resp = self._request("POST", url, params_or_data=data)
        r = mr.CreateResult(resp)

        return r

    def batch_create(self, records_or_models):
        url = self.__multiple()
        _records = [self.__to_create_format(r) for r in records_or_models]

        data = {
            "app": self.app_id,
            "records": _records
        }

        resp = self._request("POST", url, params_or_data=data)
        r = mr.BatchCreateResult(resp)

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

        data = self.__to_update_format(record_or_model)
        data["app"] = self.app_id

        resp = self._request("PUT", url, params_or_data=data)
        r = mr.UpdateResult(resp)

        return r

    def batch_update(self, records_or_models):
        url = self.__multiple()
        _records = [self.__to_update_format(r) for r in records_or_models]

        data = {
            "app": self.app_id,
            "records": _records
        }

        resp = self._request("PUT", url, params_or_data=data)
        r = mr.BatchUpdateResult(resp)

        return r

    def delete(self, record_ids_or_models, revisions=()):
        url = self.__multiple()

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

        resp = self._request("DELETE", url, params_or_data=data)
        r = mr.Result(resp)

        return r

    def __to_proceed_format(self, record_or_model, action, assignee=""):
        from enum import Enum
        record_id = -1
        revision = -1
        if self.__get_model_type(record_or_model):
            record_id = record_or_model.record_id
            revision = record_or_model.revision
        else:
            record_id = int(record_or_model["$id"]["value"])
            revision = int(record_or_model["$revision"]["value"])

        action = action
        if isinstance(action, Enum):
            action = action.value

        data = {
            "id": record_id,
            "action": action,
            "assignee": assignee
        }

        if revision > -1:
            data["revision"] = revision

        return data

    def proceed(self, record_or_model, action, assignee=""):
        url = self.API_ROOT.format(self.account.domain, "record/status.json")
        data = self.__to_proceed_format(record_or_model, action, assignee)
        data["app"] = self.app_id
        resp = self._request("PUT", url, params_or_data=data)
        r = mr.UpdateResult(resp)
        return r

    def batch_proceed(self, records_or_modesls, action, assignee=""):
        url = self.API_ROOT.format(self.account.domain, "records/status.json")
        data = [self.__to_proceed_format(rm, action, assignee) for rm in records_or_modesls]
        data = {
            "app": self.app_id,
            "records": data
        }
        resp = self._request("PUT", url, params_or_data=data)
        r = mr.BatchUpdateResult(resp)
        return r

    def administration(self):
        from pykintone.application_settings.administrator import Administrator
        return Administrator(self.account, self.api_token, self.requests_options, self.app_id)

    def comment(self, record_id):
        from pykintone.comment_api import CommentAPI
        return CommentAPI(self.account, self.app_id, record_id, self.api_token, self.requests_options)

    def __str__(self):
        info = str(self.account)
        info += "\napp:\n"
        info += "  id={0}, token={1}".format(self.app_id, self.api_token)
        return info
