import pykintone.structure as ps


class User(ps.kintoneStructure):

    def __init__(self):
        super(User, self).__init__()
        self.user_id = ""
        self.code = ""
        self.name = ""
        self.description = ""
        self.sur_name = ""
        self.sur_name_reading = ""
        self.given_name = ""
        self.given_name_reading = ""
        self.email = ""
        self.phone = ""
        self.mobile_phone = ""
        self.callto = ""
        self.url = ""
        self.employee_number = ""
        self.extension_number = ""
        self.join_date = ""
        self.birth_date = None
        self.locale = ""
        self.local_name = ""
        self.local_name_locale = ""
        self.timezone= ""
        self.primary_organization = ""
        self.sort_order = ""
        self.custom_item_values = []
        self.valid = True
        self.ctime = None
        self.mtime = None

        self._pd("user_id", field_name="id")
        self._pd("sur_name", name_style_conversion=True)
        self._pd("sur_name_reading", name_style_conversion=True)
        self._pd("given_name", name_style_conversion=True)
        self._pd("given_name_reading", name_style_conversion=True)
        self._pd("mobile_phone", name_style_conversion=True)
        self._pd("employee_number", name_style_conversion=True)
        self._pd("extension_number", name_style_conversion=True)
        self._pd("birth_date", ps.FieldType.DATE, name_style_conversion=True)
        self._pd("join_date", name_style_conversion=True)
        self._pd("local_name", name_style_conversion=True)
        self._pd("local_name_locale", name_style_conversion=True)
        self._pd("primary_organization", name_style_conversion=True)
        self._pd("sort_order", name_style_conversion=True)
        self._pd("custom_item_values", name_style_conversion=True)
        self._pd("ctime", ps.FieldType.DATETIME)
        self._pd("mtime", ps.FieldType.DATETIME)
