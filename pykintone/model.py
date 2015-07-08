import inspect


class KintoneModel():

    def __init__(self):
        self.record_id = -1
        self.revision = -1

    @classmethod
    def json_to_model(cls, record_json, model_type):
        instance = model_type()
        fields = cls.__get_fields(instance)
        get_field = lambda name: [f for f in fields if f[0] == name or "_" + f[0] == name]

        for k in record_json:
            item = record_json[k]
            value = item["value"]
            if k == "$id":
                instance.record_id = int(value)
            elif k == "$revision":
                instance.revision = int(value)
            else:
                field = get_field(k)
                if len(field) > 0:
                    f_name = field[0][0]
                    setattr(instance, f_name, value)

        return instance

    @classmethod
    def __get_fields(cls, instance):
        fields = inspect.getmembers(instance, lambda f: not (inspect.isbuiltin(f) or inspect.isroutine(f)))

        # exclude private attribute
        protecteds = [f for f in fields if not(f[0].startswith("__"))]

        return protecteds

