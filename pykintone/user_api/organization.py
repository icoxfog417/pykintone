import pykintone.structure as ps


class Organization(ps.kintoneStructure):

    def __init__(self):
        super(Organization, self).__init__()
        self.organization_id = ""
        self.code = None
        self.name = ""
        self.description = ""
        self.local_name = ""
        self.local_name_locale = ""
        self.parent_code = ""

        self._pd("organization_id", field_name="id")
        self._pd("local_name", name_style_conversion=True)
        self._pd("local_name_locale", name_style_conversion=True)
        self._pd("parent_code", name_style_conversion=True)
