import inspect
from enum import Enum
from datetime import datetime
from pykintone.account import kintoneService as ks
import pykintone.structure_field as sf


class kintoneStructure(object):

    def __init__(self):
        self._property_details = []

    @classmethod
    def _get_property_names(cls, instance):
        properties = inspect.getmembers(instance, lambda m: not (inspect.isbuiltin(m) or inspect.isroutine(m)))

        # exclude private attribute
        public_properties = [p for p in properties if not (p[0].startswith("_"))]
        names = [p[0] for p in public_properties]

        return names

    @classmethod
    def _deserialize(cls, json_body, get_value_and_type):
        """
        deserialize json to model
        :param json_body: json data
        :param get_value_and_type: function(f: json_field) -> value, field_type_string(see FieldType)
        :return:
        """

        instance = cls()
        is_set = False
        properties = cls._get_property_names(instance)

        def get_property_detail(name):
            p = [p for p in instance._property_details if p.name == name or p.field_name == name]
            return None if len(p) == 0 else p[0]

        for k in json_body:
            field = json_body[k]
            pd = get_property_detail(k)
            pn = k if not pd else pd.to_property_name(k)
            if pn in properties:
                v, t = get_value_and_type(field)
                initial_value = getattr(instance, pn)
                value = instance._field_to_property(v, t, pd, initial_value)
                setattr(instance, pn, value)
                is_set = True

        return instance if is_set else None

    @classmethod
    def _field_to_property(cls, field_value, field_type=None, property_detail=None, initial_value=None):
        value = field_value

        # configure property's field type
        # from user definition
        _field_type = None if not property_detail else property_detail.field_type
        # from type value in field
        if not _field_type and field_type:
            f = [e for e in list(FieldType) if e.value == field_type]
            if len(f) > 0:
                _field_type = f[0]
        _field_type = _field_type if _field_type else cls._estimate_type_from_property(initial_value)

        if not _field_type:
            pass
        elif _field_type in (FieldType.ID, FieldType.REVISION, FieldType.RECORD_NUMBER):
            value = int(value)
        elif _field_type == FieldType.NUMBER:
            value = float(value)
        elif _field_type == FieldType.DATE:
            value = ks.value_to_date(value)
        elif _field_type == FieldType.TIME:
            value = ks.value_to_time(value)
        elif _field_type in [FieldType.DATETIME, FieldType.CREATED_TIME, FieldType.UPDATED_TIME]:
            value = ks.value_to_datetime(value)
        elif _field_type == FieldType.TIME_STAMP:
            value = ks.value_to_timestamp(value)
        elif _field_type == FieldType.USER_SELECT:
            value = [sf.UserSelect(v["code"], v["name"]) for v in value]
        elif _field_type in [FieldType.CREATOR, FieldType.MODIFIER]:
            value = sf.UserSelect(value["code"], value["name"])
        elif _field_type == FieldType.SUBTABLE:
            if property_detail and property_detail.sub_type:
                table = []
                for r in value:
                    row = property_detail.sub_type().record_to_model(r["value"])
                    row.record_id = int(r["id"])
                    table.append(row)
                value = table
        elif _field_type == FieldType.FILE:
            pass  # todo: conversion for file
        elif _field_type == FieldType.STRUCTURE:
            cls_type = None
            if property_detail and property_detail.sub_type:
                cls_type = property_detail.sub_type
            elif initial_value:
                cls_type = cls.__get_type(initial_value)

            if cls_type:
                def deserialize(v):
                    ins = cls_type()
                    ds = getattr(ins, "deserialize", None)
                    return None if not (ds and callable(ds)) else ds(v)

                if isinstance(value, (list, tuple)):
                    value = [deserialize(v) for v in value]
                else:
                    value = deserialize(value)

        return value

    def _serialize(self, convert_to_key_and_value, ignore_missing=False):
        """
        serialize model object to dictionary
        :param convert_to_key_and_value: function(field_name, value, property_detail) -> key, value
        :return:
        """

        serialized = {}
        properties = self._get_property_names(self)

        def get_property_detail(name):
            p = [p for p in self._property_details if p.name == name]
            return None if len(p) == 0 else p[0]

        for p in properties:
            pd = get_property_detail(p)
            value = self._property_to_field(p, pd)
            field_name = p if not pd else pd.to_field_name()

            if value is None or (ignore_missing and not value) or (pd and pd.unsent):
                continue
            else:
                key, value = convert_to_key_and_value(field_name, value, pd)
                serialized[key] = value

        return serialized

    def _property_to_field(self, name, property_detail=None):
        value = getattr(self, name)
        if value is None:
            return None

        # configure field's type
        # from user definition
        field_type = None if not property_detail else property_detail.field_type
        field_type = field_type if field_type else self._estimate_type_from_property(value)

        if not field_type:
            pass
        elif field_type == FieldType.DATE:
            value = ks.date_to_value(value)
        elif field_type == FieldType.TIME:
            value = ks.time_to_value(value)
        elif field_type in [FieldType.DATETIME, FieldType.CREATED_TIME, FieldType.UPDATED_TIME, FieldType.TIME_STAMP]:
            # time stamp is same as datetime format (there is no field for timestamp in kintone)
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
        elif field_type == FieldType.STRUCTURE:
            def serialize(v):
                s = getattr(v, "serialize", None)
                return None if not (s and callable(s)) else s()

            if isinstance(value, (list, tuple)):
                value = [serialize(v) for v in value]
            else:
                value = serialize(value)

        return value

    @classmethod
    def _estimate_type_from_property(cls, value):
        field_type = None

        if isinstance(value, datetime):
            field_type = FieldType.DATE
        elif issubclass(cls.__get_type(value), kintoneStructure):
            field_type = FieldType.STRUCTURE
        elif isinstance(value, sf.UserSelect):
            field_type = FieldType.USER_SELECT

        return field_type

    @classmethod
    def __get_type(cls, value):
        get_type = lambda v: v if type(v) == type else type(v)

        if isinstance(value, (list, tuple)):
            if len(value) > 0:
                return get_type(value[0])
            else:
                return type(None)
        else:
            return get_type(value)


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
    NUMBER = "NUMBER"
    SUBTABLE = "SUBTABLE"
    CALC = "CALC"
    CATEGORY = "CATEGORY"
    CHECK_BOX = "CHECK_BOX"
    DROP_DOWN = "DROP_DOWN"
    HR = "HR"
    LABEL = "LABEL"
    LINK = "LINK"
    MULTI_LINE_TEXT = "MULTI_LINE_TEXT"
    MULTI_SELECT = "MULTI_SELECT"
    RADIO_BUTTON = "RADIO_BUTTON"
    RICH_TEXT = "RICH_TEXT"
    SINGLE_LINE_TEXT = "SINGLE_LINE_TEXT"
    SPACER = "SPACER"
    STATUS = "STATUS"
    STATUS_ASSIGNEE = "STATUS_ASSIGNEE"
    ID = "__ID__"
    REVISION = "__REVISION__"
    TIME_STAMP = "__TIME_STAMP__"
    STRUCTURE = "__STRUCTURE__"


class LayoutType(Enum):
    ROW = "ROW"
    SUBTABLE = "SUBTABLE"
    GROUP = "GROUP"
