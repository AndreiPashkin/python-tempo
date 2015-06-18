#!/usr/bin/env python
# coding=utf-8
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.six import with_metaclass
from django.db import models
import json
from tempo.schedule import Schedule
from tempo.scheduleset import ScheduleSet


class ScheduleSetField(with_metaclass(models.SubfieldBase, models.Field)):
    """DB representation of ScheduleSet. Requires PostgreSQL 9.4+."""
    def db_type(self, connection):
        return 'jsonb'

    @classmethod
    def schedule_to_dict(cls, schedule):
        return {attr: getattr(schedule, attr) for attr in
                ('years', 'months', 'days', 'weekdays', 'hours', 'minutes',
                 'seconds', 'seconds_of_the_day')}

    @classmethod
    def schedule_from_dict(cls, dictionary):
        return Schedule(**dictionary)

    @classmethod
    def schedulset_to_dict(cls, scheduleset):
        return {
            'include': map(cls.schedule_to_dict, scheduleset.include),
            'exclude': map(cls.schedule_to_dict, scheduleset.exclude)
        }

    @classmethod
    def scheduleset_from_dict(cls, dictionary):
        return ScheduleSet(
            include=map(cls.schedule_from_dict, dictionary['include']),
            exclude=map(cls.schedule_from_dict, dictionary['exclude'])
                    if 'exclude' in dictionary
                    else None
        )

    def to_python(self, value):
        if value is None:
            return value
        elif isinstance(value, ScheduleSet):
            return value
        if isinstance(value, dict):
            deserialized = value
        else:
            deserialized = json.loads(value)
        return self.scheduleset_from_dict(deserialized)

    def get_prep_lookup(self, lookup_type, value):
        return value

    def get_prep_value(self, value):
        value = super(ScheduleSetField, self).get_prep_value(value)
        if value is None:
            return None
        return json.dumps(self.schedulset_to_dict(value),
                          cls=DjangoJSONEncoder)


class Contains(models.Lookup):
    """Checks given `datetime` object for containment in
    ScheduleSet stored in DB."""
    lookup_name = 'contains'

    CONTAINMENT_CONDITION = (
        " (value->'years' @> '%(year)s'::jsonb OR "
        "  value->'years' = 'null'::jsonb) "
        " AND "
        " (value->'months' @> '%(month)s'::jsonb OR "
        "  value->'months' = 'null'::jsonb) "
        " AND "
        " ((value->'days' @> '%(day)s'::jsonb OR "
        "   value->'days' = 'null'::jsonb) "
        "  OR "
        "  (value->'weekdays' @> '%(weekday)s'::jsonb OR "
        "   value->'weekdays' = 'null'::jsonb)) "
        " AND "
        " (((value->'hours' @> '%(hour)s'::jsonb OR "
        "    value->'hours' = 'null'::jsonb) "
        "   AND "
        "  (value->'minutes' @> '%(minute)s'::jsonb OR "
        "   value->'minutes' = 'null'::jsonb) "
        "   AND "
        "  (value->'seconds' @> '%(second)s'::jsonb OR "
        "   value->'seconds' = 'null'::jsonb))"
        "  OR "
        "  (value->'seconds_of_the_day' @> '%(second_of_the_day)s'::jsonb OR "
        "   value->'seconds_of_the_day' = 'null'::jsonb))"
    )

    LOOKUP = (
        "EXISTS ("
        "    SELECT value FROM jsonb_array_elements(%(field)s->'include')"
        "    WHERE " + CONTAINMENT_CONDITION + ")"
        " AND "
        "NOT EXISTS ("
        "   SELECT value FROM jsonb_array_elements(%(field)s->'exclude')"
        "   WHERE " + CONTAINMENT_CONDITION + ")"
    )

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)

        params = {'year': self.rhs.year,
                  'month': self.rhs.month,
                  'day': self.rhs.day,
                  'weekday': self.rhs.weekday(),
                  'hour': self.rhs.hour,
                  'minute': self.rhs.minute,
                  'second': self.rhs.second,
                  'second_of_the_day': (self.rhs.hour * 60 * 60 +
                                        self.rhs.minute * 60 +
                                        self.rhs.second),
                  'field': lhs % lhs_params}
        return self.LOOKUP % params, []

ScheduleSetField.register_lookup(Contains)
