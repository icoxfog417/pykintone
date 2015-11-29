class UserAPI(object):

    def __init__(self, account, requests_options=()):
        from pykintone.user_api.export import Export
        self.for_exporting = Export(account, requests_options)