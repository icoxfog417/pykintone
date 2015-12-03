from datetime import datetime
import yaml
import pytz


class Account(object):

    def __init__(self, domain,
                 login_id="", login_password="",
                 basic_id="", basic_password=""):
        self.domain = domain
        self.login_id = login_id
        self.login_password = login_password
        self.basic_id = basic_id
        self.basic_password = basic_password

    def to_header(self, api_token="", with_content_type=True):
        header = {}
        header["Host"] = "{0}.cybozu.com:443".format(self.domain)

        def encode(user_id, password):
            import base64
            return base64.b64encode("{0}:{1}".format(user_id, password).encode(kintoneService.ENCODE))

        if self.basic_id:
            auth = encode(self.basic_id, self.basic_password)
            header["Authorization"] = "Basic {0}".format(auth)

        if api_token:
            header["X-Cybozu-API-Token"] = api_token
        elif self.login_id:
            auth = encode(self.login_id, self.login_password)
            header["X-Cybozu-Authorization"] = auth

        if with_content_type:
            header["Content-Type"] = "application/json"

        return header

    def kintone(self):
        return kintoneService(self)

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
        kintone = kintoneService(account)

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


class kintoneService(object):
    ENCODE = "utf-8"
    SELECT_LIMIT = 500
    UPDATE_LIMIT = 100

    DATE_FORMAT = "%Y-%m-%d"
    TIME_FORMAT = "%H:%M"
    DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
    TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
    from tzlocal import get_localzone
    __TIME_ZONE = get_localzone()

    def __init__(self, account):
        self.account = account
        self.__apps = []

    def __len__(self):
        return len(self.__apps)

    def app(self, app_id="", api_token="", app_name=""):
        from pykintone.application import Application
        if not app_id:
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

    def administration(self,requests_options=()):
        from pykintone.application_settings.administrator import Administrator
        return Administrator(self.account, requests_options=requests_options)

    def user_api(self, requests_options=()):
        from pykintone.user_api import UserAPI
        api = UserAPI(self.account, requests_options)
        return api

    @classmethod
    def value_to_date(cls, value):
        return value if not value else datetime.strptime(value, cls.DATE_FORMAT)

    @classmethod
    def value_to_time(cls, value):
        return value if not value else datetime.strptime(value, cls.TIME_FORMAT)

    @classmethod
    def value_to_datetime(cls, value):
        if value:
            d = datetime.strptime(value, cls.DATETIME_FORMAT)
            return cls._to_local(d)
        else:
            return None

    @classmethod
    def value_to_timestamp(cls, value):
        if value:
            d = datetime.strptime(value, cls.TIMESTAMP_FORMAT)
            return cls._to_local(d)
        else:
            return None

    @classmethod
    def _to_local(cls, d):
        utc = d.replace(tzinfo=pytz.utc)  # configure timezone (on kintone, time is utc)
        local = utc.astimezone(cls.__TIME_ZONE).replace(tzinfo=None)  # to local, and to native
        return local

    @classmethod
    def date_to_value(cls, date):
        return date.strftime(cls.DATE_FORMAT)

    @classmethod
    def time_to_value(cls, time):
        return time.strftime(cls.TIME_FORMAT)

    @classmethod
    def datetime_to_value(cls, dt):
        local = dt.replace(tzinfo=cls.__TIME_ZONE)
        utc = local.astimezone(pytz.utc)
        value = utc.strftime(cls.DATETIME_FORMAT)
        return value

    @classmethod
    def get_default_field_list(cls, as_str=False):
        from pykintone.structure import FieldType
        fields = [
            FieldType.CATEGORY,
            FieldType.STATUS,
            FieldType.RECORD_NUMBER,
            FieldType.CREATED_TIME,
            FieldType.CREATOR,
            FieldType.STATUS_ASSIGNEE,
            FieldType.UPDATED_TIME,
            FieldType.MODIFIER
        ]
        if as_str:
            str_fields = [f.value for f in fields]
            return str_fields
        else:
            return fields

