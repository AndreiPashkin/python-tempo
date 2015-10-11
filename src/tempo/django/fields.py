# coding=utf-8
"""Provides Django model fields API for RecurrentEventSet."""
import json

from django.utils.six import with_metaclass
from django.db import models

from tempo.recurrenteventset import RecurrentEventSet
# pylint: disable=no-init,no-self-use,no-member,super-on-old-class
# pylint: disable=missing-docstring


class RecurrentEventSetField(with_metaclass(models.SubfieldBase,
                                            models.Field)):
    """DB representation of recurrenteventset. Requires PostgreSQL 9.4+."""

    def db_type(self, connection):  # pylint: disable=unused-argument
        return 'jsonb'

    def to_python(self, value):
        if value is None or value == '':
            return None
        elif isinstance(value, RecurrentEventSet):
            return value

        return RecurrentEventSet.from_json(value)

    def get_prep_lookup(self, lookup_type, value):
        # We only handle 'exact' and 'in'. All others are errors.
        if lookup_type == 'contains':
            return value.isoformat()
        elif lookup_type == 'intersects' or lookup_type == 'occurs_within':
            return (value[0].isoformat(), value[1].isoformat())
        else:
            raise TypeError('Lookup type %r not supported.' % lookup_type)

    def get_prep_value(self, value):
        value = super(RecurrentEventSetField, self).get_prep_value(value)
        if value is None:
            return None
        return json.dumps(value.to_json())


class Contains(models.Lookup):
    """Checks a single `datetime` object for containment in
    RecurrentEventSet."""
    lookup_name = 'contains'

    def as_sql(self, compiler, connection):
        lhs, _ = self.process_lhs(compiler, connection)
        rhs, _ = self.process_rhs(compiler, connection)

        return ('tempo_recurrenteventset_contains('
                '    %s::tempo_recurrenteventset, %s::timestamp'
                ')' %
                (lhs, rhs),
                (self.rhs,))

RecurrentEventSetField.register_lookup(Contains)


class Intersects(models.Lookup):
    """Checks a given time interval in form of a pair-tuple of ``datetime``
    objects, intersects with time defined by time interval set in
    given column."""
    lookup_name = 'intersects'

    def as_sql(self, compiler, connection):
        lhs, _ = self.process_lhs(compiler, connection)
        rhs, _ = self.process_rhs(compiler, connection)

        start, stop = self.rhs

        return ("""(SELECT bool_and(start < %s AND stop > %s) FROM
                    tempo_recurrenteventset_forward(
                        %s::tempo_recurrenteventset, %s::timestamp, 1
                    ))
                """ % (rhs, rhs, lhs, rhs), (stop, start, start))

RecurrentEventSetField.register_lookup(Intersects)


class OccursWithin(models.Lookup):
    """Checks if some of continous events, defined in time interval set
    is enclosed by dates in given pair-tuple of datetime objects."""
    lookup_name = 'occurs_within'

    def as_sql(self, compiler, connection):
        lhs, _ = self.process_lhs(compiler, connection)
        rhs, _ = self.process_rhs(compiler, connection)

        start, stop = self.rhs

        return ("""(SELECT bool_and(start >= %s AND stop <= %s) FROM
                    tempo_recurrenteventset_forward(
                        %s::tempo_recurrenteventset, %s::timestamp, 1,
                        false
                    ))
                """ % (rhs, rhs, lhs, rhs), (start, stop, start))

RecurrentEventSetField.register_lookup(OccursWithin)
