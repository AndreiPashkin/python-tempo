#!/usr/bin/env python
# coding=utf-8
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.six import with_metaclass
from django.db import models
import json
from tempo.scheduleset import ScheduleSet


class ScheduleSetField(with_metaclass(models.SubfieldBase, models.Field)):
    """DB representation of ScheduleSet. Requires PostgreSQL 9.4+."""
    def db_type(self, connection):
        return 'jsonb'

    def to_python(self, value):
        if isinstance(value, ScheduleSet):
            return value
        if isinstance(value, dict):
            deserialized = value
        else:
            deserialized = json.loads(value)
        return ScheduleSet.from_dict(deserialized)

    def get_prep_lookup(self, lookup_type, value):
        return value

    def get_prep_value(self, value):
        value = super(ScheduleSetField, self).get_prep_value(value)
        if value is None:
            return None
        return json.dumps(value.to_dict(), cls=DjangoJSONEncoder)


class Contains(models.Lookup):
    """Checks given `datetime` object for containment in
    ScheduleSet stored in DB."""
    lookup_name = 'contains'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)

        lookup = (
            "EXISTS ("
            "   SELECT value FROM jsonb_array_elements(%(field)s->'include')"
            "   WHERE (value->'years' @> '%(year)s'::jsonb OR "
            "          value->'years' = 'null'::jsonb) AND "
            "         (value->'months' @> '%(month)s'::jsonb OR "
            "          value->'months' = 'null'::jsonb) AND "
            "         (value->'days' @> '%(day)s'::jsonb OR "
            "          value->'days' = 'null'::jsonb) AND "
            "         (value->'hours' @> '%(hour)s'::jsonb OR "
            "          value->'hours' = 'null'::jsonb) AND "
            "         (value->'minutes' @> '%(minute)s'::jsonb OR "
            "          value->'minutes' = 'null'::jsonb) AND "
            "         (value->'seconds' @> '%(second)s'::jsonb OR "
            "          value->'seconds' = 'null'::jsonb)"
            ") AND "
            "NOT EXISTS ("
            "   SELECT value FROM jsonb_array_elements(%(field)s->'exclude')"
            "   WHERE (value->'years' @> '%(year)s'::jsonb OR "
            "          value->'years' = 'null'::jsonb) AND "
            "         (value->'months' @> '%(month)s'::jsonb OR "
            "          value->'months' = 'null'::jsonb) AND "
            "         (value->'days' @> '%(day)s'::jsonb OR "
            "          value->'days' = 'null'::jsonb) AND "
            "         (value->'hours' @> '%(hour)s'::jsonb OR "
            "          value->'hours' = 'null'::jsonb) AND "
            "         (value->'minutes' @> '%(minute)s'::jsonb OR "
            "          value->'minutes' = 'null'::jsonb) AND "
            "         (value->'seconds' @> '%(second)s'::jsonb OR "
            "          value->'seconds' = 'null'::jsonb)"
            ")"
        )
        params = {'year': self.rhs.year,
                  'month': self.rhs.month,
                  'day': self.rhs.day,
                  'hour': self.rhs.hour,
                  'minute': self.rhs.minute,
                  'second': self.rhs.second,
                  'field': lhs % lhs_params}
        return lookup % params, []

ScheduleSetField.register_lookup(Contains)
