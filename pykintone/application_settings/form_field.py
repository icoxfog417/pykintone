import pykintone.structure as ps


class BaseField(ps.kintoneStructure):

    def __init__(self):
        super(BaseField, self).__init__()
        self.field_type = ""
        self.code = ""
        self._property_details.append(ps.PropertyDetail("field_type", field_name="type"))

    def serialize(self):
        return self._serialize(lambda name, value, pd: (name, value))

    @classmethod
    def deserialize(cls, json_body):
        return cls._deserialize(json_body, lambda f: (f, ""))


class Label(BaseField):

    def __init__(self):
        super(Label, self).__init__()
        self.label = ""


class BaseFormField(BaseField):

    def __init__(self):
        super(BaseFormField, self).__init__()
        self.label = ""
        self.no_label = False
        self.required = False
        self.default_value = ""

        self._property_details.append(ps.PropertyDetail("no_label", field_name="noLabel"))
        self._property_details.append(ps.PropertyDetail("default_value", field_name="defaultValue"))

    @classmethod
    def create(cls, field_type, code, label, no_label=False, required=False, default_value=""):
        f = BaseFormField()
        f.field_type = field_type
        f.code = code
        f.label = label
        f.no_label = no_label
        f.required = required
        f.default_value = default_value
        return f
