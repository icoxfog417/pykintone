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
        def get_value_and_type(f): return f["value"], f["type"]
        return cls._deserialize(record_json, get_value_and_type)

    def to_record(self):
        def convert_to_key_and_value(field_name, value, property_detail=None):
            key = field_name
            formatted = {
                "value": value
            }
            if field_name in ["$id", "$revision"]:
                if value > -1:
                    key = field_name[1:]  # escape $
                else:
                    key = None

            return key, formatted

        return self._serialize(convert_to_key_and_value)
