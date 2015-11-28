import pykintone.structure as ps


class Group(ps.kintoneStructure):

    def __init__(self):
        super(Group, self).__init__()
        self.group_id = ""
        self.code = None
        self.name = ""
        self.description = ""

        self._pd("group_id", field_name="id")
