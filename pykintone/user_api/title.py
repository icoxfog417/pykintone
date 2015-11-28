import pykintone.structure as ps


class Title(ps.kintoneStructure):

    def __init__(self):
        super(Title, self).__init__()
        self.title_id = ""
        self.code = None
        self.name = ""
        self.description = ""

        self._pd("title_id", field_name="id")
