from pykintone.result import Result


class GetUsersResult(Result):

    def __init__(self, response):
        super(GetUsersResult, self).__init__(response)
        self.raw = []
        self.users = []
        if self.ok:
            serialized = response.json()
            if "users" in serialized:
                self.raw = serialized["users"]
                from pykintone.user_api.user import User
                self.users = [User.deserialize(u) for u in self.raw]


class UserOrganizationTitlesResult(Result):

    def __init__(self, response):
        super(UserOrganizationTitlesResult, self).__init__(response)
        self.raw = []
        self.organization_titles = []
        if self.ok:
            serialized = response.json()
            if "organizationTitles" in serialized:
                self.raw = serialized["organizationTitles"]
                from pykintone.user_api.organization import Organization
                from pykintone.user_api.title import Title
                from collections import namedtuple
                OrganizationTitle = namedtuple("OrganizationTitle", ["organization", "title"])
                for ot in self.raw:
                    o = Organization.deserialize(ot["organization"])
                    t = None
                    if ot["title"] is not None:
                        t = Title.deserialize(ot["title"])
                    self.organization_titles.append(OrganizationTitle(o, t))


class GetUserGroupsResult(Result):

    def __init__(self, response):
        super(GetUserGroupsResult, self).__init__(response)
        self.raw = []
        self.groups = []
        if self.ok:
            serialized = response.json()
            if "groups" in serialized:
                self.raw = serialized["groups"]
                from pykintone.user_api.group import Group
                self.groups = [Group.deserialize(u) for u in self.raw]
