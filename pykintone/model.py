import inspect
from enum import Enum
from collections import namedtuple
from datetime import datetime
from pykintone.account import kintoneService as ks


class kintoneModel(object):
    def __init__(self):
        self.record_id = -1
        self.revision = -1
        self._property_details = []
        self._property_details.append(PropertyDetail("record_id", field_name="$id"))
        self._property_details.append(PropertyDetail("revision", field_name="$revision"))

    @classmethod
    def record_to_model(cls, record_json):
        instance = cls()
        is_set = False
        properties = cls.__get_property_names(instance)

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
        properties = self.__get_property_names(self)

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

    @classmethod
    def __get_property_names(cls, instance):
        properties = inspect.getmembers(instance, lambda m: not (inspect.isbuiltin(m) or inspect.isroutine(m)))

        # exclude private attribute
        public_properties = [p for p in properties if not (p[0].startswith("_"))]
        names = [p[0] for p in public_properties]

        return names

    @classmethod
    def field_to_property(cls, field, property_detail=None):
        value = field["value"]

        # configure property's field type
        # from user definition
        field_type = None if not property_detail else property_detail.field_type
        # from type value in field
        if not field_type:
            f = [e for e in list(FieldType) if e.value == field["type"]]
            if len(f) > 0:
                field_type = f[0]

        if not field_type:
            pass
        elif field_type in (FieldType.ID, FieldType.REVISION, FieldType.RECORD_NUMBER):
            value = int(value)
        elif field_type == FieldType.NUMBER:
            value = float(value)
        elif field_type == FieldType.DATE:
            value = ks.value_to_date(value)
        elif field_type == FieldType.TIME:
            value = ks.value_to_time(value)
        elif field_type in [FieldType.DATETIME, FieldType.CREATED_TIME, FieldType.UPDATED_TIME]:
            value = ks.value_to_datetime(value)
        elif field_type == FieldType.USER_SELECT:
            value = [UserSelect(v["code"], v["name"]) for v in value]
        elif field_type in [FieldType.CREATOR, FieldType.MODIFIER]:
            value = UserSelect(value["code"], value["name"])
        elif field_type == FieldType.SUBTABLE:
            if property_detail and property_detail.sub_type:
                table = []
                for r in value:
                    row = property_detail.sub_type().record_to_model(r["value"])
                    row.record_id = int(r["id"])
                    table.append(row)
                value = table
        elif field_type == FieldType.FILE:
            pass  # todo: conversion for file

        return value

    def property_to_field(self, name, property_detail=None):
        value = getattr(self, name)
        if value is None:
            return None

        # configure field's type
        # from user definition
        field_type = None if not property_detail else property_detail.field_type
        # from property's value class
        if not field_type:
            if isinstance(value, datetime):
                field_type = FieldType.DATE

        if not field_type:
            pass
        elif field_type == FieldType.DATE:
            value = ks.date_to_value(value)
        elif field_type == FieldType.TIME:
            value = ks.time_to_value(value)
        elif field_type in [FieldType.DATETIME, FieldType.CREATED_TIME, FieldType.UPDATED_TIME]:
            value = ks.datetime_to_value(value)
        elif field_type == FieldType.USER_SELECT:
            value = [{"code": u.code} for u in value]
        elif field_type in [FieldType.CREATOR, FieldType.MODIFIER]:
            value = {"code": value.code}
        elif field_type == FieldType.SUBTABLE:
            if property_detail and property_detail.sub_type:
                table = []
                for r in value:
                    table.append({
                        "value": r.to_record()
                    })
                value = table
        elif field_type == FieldType.FILE:
            pass  # todo: conversion for file

        return value


class PropertyDetail(object):
    def __init__(self, name, field_type=None, sub_type=None, unsent=False, field_name=""):
        self.name = name
        self.field_type = field_type
        self.sub_type = sub_type
        self.unsent = unsent
        self.field_name = field_name

    def to_property_name(self, field_name):
        if self.field_name == field_name:
            return self.name
        else:
            return field_name

    def to_field_name(self):
        if self.field_name:
            return self.field_name
        else:
            return self.name


class FieldType(Enum):
    DATE = "DATE"
    TIME = "TIME"
    DATETIME = "DATETIME"
    CREATED_TIME = "CREATED_TIME"
    UPDATED_TIME = "UPDATED_TIME"
    USER_SELECT = "USER_SELECT"
    CREATOR = "CREATOR"
    MODIFIER = "MODIFIER"
    FILE = "FILE"
    RECORD_NUMBER = "RECORD_NUMBER"
    ID = "__ID__"
    REVISION = "__REVISION__"
    NUMBER = "NUMBER"
    SUBTABLE = "SUBTABLE"


UserSelect = namedtuple("UserSelect", ["code", "name"])
