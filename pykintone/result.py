from collections import namedtuple


class Result():

    def __init__(self, response):
        self.ok = response.ok
        self.message = ""
        if not self.ok:
            self.error = response.json()
            self.message = self.error["message"]


class SelectSingleResult(Result):

    def __init__(self, response):
        super(SelectSingleResult, self).__init__(response)
        self.record = {}
        if self.ok:
            self.record = response.json()


class SelectResult(Result):

    def __init__(self, response):
        super(SelectResult, self).__init__(response)
        self.records = []
        if self.ok:
            self.records = response.json()


RecordKey = namedtuple("RecordInfo", ["record_id", "revision"])


class CreateSingleResult(Result):

    def __init__(self, response):
        super(CreateSingleResult, self).__init__(response)
        self.key = {}
        if self.ok:
            _key = response.json()
            self.key = RecordKey(int(_key["id"]), int(_key["revision"]))


class UpdateSingleResult(Result):

    def __init__(self, response):
        super(UpdateSingleResult, self).__init__(response)
        self.revision = -1
        if self.ok:
            _info = response.json()
            self.revision = int(_info["revision"])


class CreateResult(Result):

    def __init__(self, response):
        super(CreateResult, self).__init__(response)
        self.keys = []
        if self.ok:
            _keys = response.json()
            for i, r_id in enumerate(_keys["ids"]):
                k = RecordKey(int(_keys["ids"][i]), int(_keys["revisions"][i]))
                self.keys.append(k)


class UpdateResult(Result):

    def __init__(self, response):
        super(UpdateResult, self).__init__(response)
        self.keys = []
        if self.ok:
            _keys = response.json()
            for r in _keys["records"]:
                k = RecordKey(int(r["id"]), int(r["revision"]))
                self.keys.append(k)
