import pykintone.structure as ps


class Layout(ps.kintoneStructure):

    def __init__(self):
        super(Layout, self).__init__()
        self.layout_type = "ROW"
        self.code = ""
        self.fields = [LayoutField]
        self._property_details.append(ps.PropertyDetail("layout_type", field_name="type"))

    @classmethod
    def create(cls, fields, layout_type="", code=""):
        instance = Layout()
        instance.layout_type = layout_type if layout_type else instance.layout_type
        instance.code = code if code else instance.code

        if not (isinstance(fields, (list, tuple)) and len(fields) > 0):
            raise Exception("Layout fields have to be array, and it must have at least one field.")

        def convert(f):
            if isinstance(f, LayoutField):
                return f
            elif isinstance(f, (list, tuple)):
                return LayoutField.create(*f)
            elif isinstance(f, dict):
                return LayoutField.create(**f)
            else:
                return LayoutField.create(f)

        fs = [convert(f) for f in fields]
        instance.fields = fs
        return instance

    def serialize(self):
        return self._serialize(lambda name, value, pd: (name, value), ignore_missing=True)

    @classmethod
    def deserialize(cls, json_body):
        return cls._deserialize(json_body, lambda f: (f, ""))


class LayoutField(ps.kintoneStructure):

    def __init__(self):
        super(LayoutField, self).__init__()
        self.field_type = ""
        self.code = ""
        self.label = ""
        self.element_id = ""
        self.size = LayoutFieldSize()
        self._pd("field_type", field_name="type")
        self._pd("element_id", name_style_conversion=True)

    @classmethod
    def create(cls, field_or_field_type, code="", width=0, height=0, inner_height=0):
        from pykintone.application_settings.form_field import BaseField
        f = None

        if isinstance(field_or_field_type, BaseField):
            f = field_or_field_type.to_layout_field()
        else:
            f.field_type = field_or_field_type
            f.code = code

        f.size.width = width if width else f.size.width
        f.size.height = height if height else f.size.height
        f.size.inner_height = inner_height if inner_height else f.size.inner_height
        return f

    def serialize(self):
        return self._serialize(lambda name, value, pd: (name, value), ignore_missing=True)

    @classmethod
    def deserialize(cls, json_body):
        return cls._deserialize(json_body, lambda f: (f, ""))


class LayoutFieldSize(ps.kintoneStructure):

    def __init__(self):
        super(LayoutFieldSize, self).__init__()
        self.width = 0
        self.height = 0
        self.inner_height = 0
        self._pd("inner_height", name_style_conversion=True)

    def serialize(self):
        return self._serialize(lambda name, value, pd: (name, value), ignore_missing=True)

    @classmethod
    def deserialize(cls, json_body):
        s = cls._deserialize(json_body, lambda f: (f, ""))
        s.width = float(s.width)
        s.height = float(s.height)
        s.inner_height = float(s.inner_height)
        return s
