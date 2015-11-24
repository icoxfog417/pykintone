from collections import namedtuple
from pykintone.result import Result


class SelectSingleResult(Result):

    def __init__(self, response):
        super(SelectSingleResult, self).__init__(response)
        self.record = {}
        if self.ok:
            serialized = response.json()
            if "record" in serialized:
                self.record = serialized["record"]

    def model(self, model_type):
        return model_type.record_to_model(self.record)


class SelectResult(Result):

    def __init__(self, response):
        super(SelectResult, self).__init__(response)
        self.records = []
        self.total_count = 0
        if self.ok:
            serialized = response.json()
            if "records" in serialized:
                self.records = serialized["records"]
            if "totalCount" in serialized:
                self.total_count = int(serialized["totalCount"])

    def models(self, model_type):
        ms = [model_type.record_to_model(r) for r in self.records]
        ms = [m for m in ms if m]
        return ms


RecordKey = namedtuple("RecordKey", ["record_id", "revision"])


class CreateResult(Result):

    def __init__(self, response):
        super(CreateResult, self).__init__(response)
        self.record_id = -1
        self.revision = -1
        if self.ok:
            _key = response.json()
            self.record_id = int(_key["id"])
            self.revision = int(_key["revision"])


class BatchCreateResult(Result):

    def __init__(self, response):
        super(BatchCreateResult, self).__init__(response)
        self.keys = []
        if self.ok:
            _keys = response.json()
            for i, r_id in enumerate(_keys["ids"]):
                k = RecordKey(int(_keys["ids"][i]), int(_keys["revisions"][i]))
                self.keys.append(k)


class UpdateResult(Result):

    def __init__(self, response):
        super(UpdateResult, self).__init__(response)
        self.revision = -1
        if self.ok:
            _info = response.json()
            self.revision = int(_info["revision"])


class BatchUpdateResult(Result):

    def __init__(self, response):
        super(BatchUpdateResult, self).__init__(response)
        self.keys = []
        if self.ok:
            _keys = response.json()
            for r in _keys["records"]:
                k = RecordKey(int(r["id"]), int(r["revision"]))
                self.keys.append(k)

