from os.path import basename


class UserSelect(object):

    def __init__(self, code="", name=""):
        self.code = code
        self.name = name

    def serialize(self):
        if self.code:
            return {
                "code": self.code
            }
        else:
            return None

    @classmethod
    def deserialize(cls, json_body):
        j = json_body
        return UserSelect(
            j["code"],
            j["name"]
        )


class File(object):
    API_ROOT = "https://{0}.cybozu.com/k/v1/file.json"

    def __init__(self, content_type="", file_key="", name="", size=0.0):
        self.content_type = content_type
        self.file_key = file_key
        self.name = name
        self.size = size
        self.file = None

    def serialize(self):
        if self.file_key:
            return {
                "fileKey": self.file_key
            }
        else:
            return None

    @classmethod
    def deserialize(cls, json_body):
        j = json_body
        return File(
            j["contentType"],
            j["fileKey"],
            j["name"],
            float(j["size"])
        )

    def download(self, api, cache_enable=False):
        if cache_enable and self.file:
            return self.file

        url = self.API_ROOT.format(api.account.domain)
        r = api._request("GET", url, params_or_data={"fileKey": self.file_key})

        file = None
        if r.ok:
            file = r.content
            self.file = file
            self.content_type = r.headers.get("content-type")

        return file

    @classmethod
    def upload(cls, file_or_path, api, file_name="", mime_type=""):
        url = cls.API_ROOT.format(api.account.domain)

        def _upload(kfile):
            if file_name:
                n = file_name
            else:
                n = "" if not hasattr(kfile, "name") else basename(kfile.name)

            f = {"file": (n, kfile, mime_type) if mime_type else (n, kfile)}
            r = api._request("FILE", url, params_or_data=f)
            return n, r

        resp = None
        if isinstance(file_or_path, str):
            with open(file_or_path, "rb") as f:
                name, resp = _upload(f)
        else:
            name, resp = _upload(file_or_path)

        uploaded = None
        if resp.ok:
            body = resp.json()
            if "fileKey" in body:
                uploaded = File(name=name, file_key=body["fileKey"])
        else:
            print(resp.json())

        return uploaded
