import pykintone.structure as ps


class kintoneModel(ps.kintoneStructure):

    def __init__(self):
        super(kintoneModel, self).__init__()
        self.record_id = -1
        self.revision = -1
        self._property_details.append(ps.PropertyDetail("record_id", field_name="$id"))
        self._property_details.append(ps.PropertyDetail("revision", field_name="$revision"))

    @classmethod
    def record_to_model(cls, record_json):
        instance = cls()
        is_set = False
        properties = cls._get_property_names(instance)

        def get_property_detail(name):
            p = [p for p in instance._property_details if p.name == name or p.field_name == name]
            return None if len(p) == 0 else p[0]

        for k in record_json:
            field = record_json[k]
            pd = get_property_detail(k)
            pn = k if not pd else pd.to_property_name(k)
            if pn in properties:
                value = instance.field_to_property(field, pd)
                setattr(instance, pn, value)
                is_set = True

        return instance if is_set else None

    def to_record(self):
        record = {}
        properties = self._get_property_names(self)

        def get_property_detail(name):
            p = [p for p in self._property_details if p.name == name]
            return None if len(p) == 0 else p[0]

        for p in properties:
            pd = get_property_detail(p)
            value = self.property_to_field(p, pd)
            fn = p if not pd else pd.to_field_name()
            if value is not None and not (pd and pd.unsent):
                formatted = {
                    "value": value
                }
                if fn in ["$id", "$revision"]:
                    if value > -1:
                        record[fn[1:]] = formatted  # escape $
                else:
                    record[fn] = formatted

        return record
