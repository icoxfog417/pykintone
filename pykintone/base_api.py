import json
import requests


class BaseAPI(object):

    def __init__(self, account, api_token="", requests_options=(), app_id=""):
        self.account = account
        self.api_token = api_token
        self.requests_options = {} if len(requests_options) == 0 else requests_options
        self.app_id = app_id

    def _request(self, method, url, params_or_data, headers=None, use_api_token=True):
        m = method.upper()
        h = headers
        token = self.api_token if use_api_token else ""
        r = None

        if m == "GET":
            h = h if h else self.account.to_header(api_token=token, with_content_type=False)
            r = requests.get(url, params=params_or_data, headers=h, **self.requests_options)
        elif m == "FILE":
            h = h if h else self.account.to_header(api_token=token, with_content_type=False)
            r = requests.request("POST", url, files=params_or_data, headers=h, **self.requests_options)
        else:
            h = h if h else self.account.to_header(api_token=token)
            r = requests.request(m, url, data=json.dumps(params_or_data), headers=h, **self.requests_options)

        return r
