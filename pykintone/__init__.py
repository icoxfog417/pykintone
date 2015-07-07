from pykintone.api import Account


def load(path):
    apps = Account.load(path)
    return apps
