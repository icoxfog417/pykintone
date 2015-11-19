from collections import namedtuple


Error = namedtuple("Error", ["message", "id", "code"])


class Result(object):

    def __init__(self, response):
        self.ok = response.ok
        self.message = ""
        self.error = None
        if not self.ok:
            _e = response.json()
            self.error = Error(_e["message"], _e["id"], _e["code"])
            self.detail = {}
            if "errors" in _e:
                self.detail = _e["errors"]
