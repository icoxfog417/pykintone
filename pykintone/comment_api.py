import json
import requests
import pykintone.comment_result as cr
from pykintone.comment import Mention


class CommentAPI(object):
    API_ROOT = "https://{0}.cybozu.com/k/v1/record/comment.json"

    def __init__(self, account, app_id, record_id, api_token="", requests_options=()):
        self.account = account
        self.app_id = app_id
        self.record_id = record_id
        self.api_token = api_token
        self.requests_options = {} if len(requests_options) == 0 else requests_options
        self._url = self.API_ROOT.format(self.account.domain)

    def select(self, order_asc=None, offset=-1, limit=-1):
        url = self._url.replace("comment.json", "comments.json")
        data = {
            "app": self.app_id,
            "record": self.record_id
        }

        if order_asc is not None:
            if order_asc:
                data["order"] = "asc"
            else:
                data["order"] = "desc"

        if offset > -1:
            data["offset"] = offset

        if limit > -1:
            data["limit"] = limit

        resp = self._request("GET", url, data)
        r = cr.SelectCommentResult(resp)
        return r


    def create(self, comment, mentions=()):
        """
        create comment
        :param comment:
        :param mentions: list of pair of code and type("USER", "GROUP", and so on)
        :return:
        """

        data = {
            "app": self.app_id,
            "record": self.record_id,
            "comment": {
                "text": comment,
            }
        }

        if len(mentions) > 0:
            _mentions = []
            for m in mentions:
                if isinstance(m, (list, tuple)):
                    if len(m) == 2:
                        _mentions.append({
                            "code": m[0],
                            "type": m[1]
                        })
                    else:
                        raise Exception("mention have to have code and target type. ex.[('user_1', 'USER')]")
                elif isinstance(m, Mention):
                    _mentions.append(m.serialize())

            data["comment"]["mentions"] = _mentions

        resp = self._request("POST", self._url, data)
        r = cr.CreateCommentResult(resp)
        return r

    def delete(self, comment_id):

        data = {
            "app": self.app_id,
            "record": self.record_id,
            "comment": comment_id
        }

        resp = self._request("DELETE", self._url, data)
        r = cr.Result(resp)
        return r


    def _request(self, method, url, params_or_data, headers=None, use_api_token=True):
        m = method.upper()
        h = headers
        token = self.api_token if use_api_token else ""
        r = None

        if m == "GET":
            h = h if h else self.account.to_header(api_token=token, with_content_type=False)
            r = requests.get(url, params=params_or_data, headers=h, **self.requests_options)
        else:
            h = h if h else self.account.to_header(api_token=token)
            r = requests.request(m, url, data=json.dumps(params_or_data), headers=h, **self.requests_options)

        return r
