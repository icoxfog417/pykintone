import inspect
from enum import Enum


class kintoneModel():

    def __init__(self):
        self.record_id = -1
        self.revision = -1

    @classmethod
    def record_to_model(cls, record_json):
        instance = cls()
        fields = cls.__get_field_names(instance)
        is_set = False

        for k in record_json:
            item = record_json[k]
            value = item["value"]
            if k == "$id":
                instance.record_id = int(value)
            elif k == "$revision":
                instance.revision = int(value)
            else:
                if k in fields:
                    setattr(instance, k, value)

            is_set = True

        return instance if is_set else None

    def to_record(self):
        fields = self.__get_field_names(self)
        record = {}

        for f in fields:
            value = getattr(self, f)
            if f == "record_id":
                record["id"] = value
            else:
                record[f] = value

        return record

    @classmethod
    def __get_field_names(cls, instance):
        fields = inspect.getmembers(instance, lambda f: not (inspect.isbuiltin(f) or inspect.isroutine(f)))

        # exclude private attribute
        public_fields = [f for f in fields if not(f[0].startswith("_"))]
        names = [f[0] for f in public_fields]

        return names
