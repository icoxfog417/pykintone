from pykintone.account import Account, kintoneService


def load(path):
    kintone = Account.load(path)
    return kintone


def login(domain,
          login_id, login_password,
          basic_id="", basic_password=""):

    account = Account(domain,
                      login_id, login_password,
                      basic_id, basic_password)

    kintone = kintoneService(account)

    return kintone


def app(domain, app_id, api_token, app_name=""):
    kintone = kintoneService(Account(domain))
    return kintone.app(app_id, api_token, app_name)
