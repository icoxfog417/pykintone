import pykintone.structure as ps


class BaseField(ps.kintoneStructure):

    def __init__(self):
        super(BaseField, self).__init__()

    def serialize(self):
        return self._serialize(lambda name, value, pd: (name, value))

    @classmethod
    def deserialize(cls, json_body):
        return cls._deserialize(json_body, lambda f: (f[0], f[1]))


class BaseFormField(BaseField):

    def __init__(self):
        super(BaseFormField, self).__init__()
        self.label = ""
        self.field_type = ""
        self.code = ""
        self.no_label = False
        self.required = False
        self.default_value = ""

        self._property_details.append(ps.PropertyDetail("field_type", field_name="type"))
        self._property_details.append(ps.PropertyDetail("no_label", field_name="noLabel"))
        self._property_details.append(ps.PropertyDetail("default_value", field_name="defaultValue"))

    @classmethod
    def deserialize(cls, json_body):
        return cls._deserialize(json_body, lambda f: (f, ""))


class Label(BaseField):

    def __init__(self):
        super(Label, self).__init__()
        self.label = ""
        self.field_type = ""

        self._property_details.append(ps.PropertyDetail("field_type", field_name="type"))
