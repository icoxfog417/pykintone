import inspect
from enum import Enum
from collections import namedtuple
from pykintone.account import kintoneService as ks


class kintoneModel():

    def __init__(self):
        self.record_id = -1
        self.revision = -1
        self._field_types = {}

    @classmethod
    def record_to_model(cls, record_json):
        instance = cls()
        properties = cls.__get_property_names(instance)
        is_set = False

        for k in record_json:
            item = record_json[k]
            value = instance.field_to_property(k, item)
            if k == "$id":
                instance.record_id = int(value)
            elif k == "$revision":
                instance.revision = int(value)
            else:
                if k in properties:
                    setattr(instance, k, value)

            is_set = True

        return instance if is_set else None

    def to_record(self):
        properties = self.__get_property_names(self)
        properties = [p for p in properties if not(p in self._field_types and self._field_types[p] == FieldType.not_upload)]
        record = {}

        for p in properties:
            value = getattr(self, p)
            if value is not None:
                value = self.property_to_field(p, value)
                formatted = {
                    "value": value
                }
                if p == "record_id":
                    record["id"] = formatted
                else:
                    record[p] = formatted

        return record

    @classmethod
    def __get_property_names(cls, instance):
        properties = inspect.getmembers(instance, lambda m: not (inspect.isbuiltin(m) or inspect.isroutine(m)))

        # exclude private attribute
        public_properties = [p for p in properties if not(p[0].startswith("_"))]
        names = [p[0] for p in public_properties]

        return names

    def field_to_property(self, field_name, field):
        value = field["value"]
        field_type = None
        if field_name in self._field_types:
            field_type = self._field_types[field_name]

        if not field_type:
            pass
        elif field_type in (FieldType.ID, FieldType.REVISION, FieldType.RECORD_NUMBER):
            value = int(value)
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
            pass  # todo: conversion for subtable
        elif field_type == FieldType.FILE:
            pass  # todo: conversion for file

        return value

    def property_to_field(self, name, value):
        from datetime import datetime
        value = getattr(self, name)

        field_type = None
        if name in self._field_types:
            field_type = self._field_types[name]
        elif isinstance(value, datetime):
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
            value = {
                "code": value.code
            }
        elif field_type == FieldType.SUBTABLE:
            pass  # todo: conversion for subtable
        elif field_type == FieldType.FILE:
            pass  # todo: conversion for file

        return value

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
    not_upload = "not_upload"

UserSelect = namedtuple("UserSelect", ["code", "name"])
