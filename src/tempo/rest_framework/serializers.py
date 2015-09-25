# coding=utf-8
"""Provides utilities for serialization/deserialization of
Tempo data types.
"""
from six import string_types

from rest_framework import serializers

from tempo.timeintervalset import TimeIntervalSet


# pylint: disable=no-init,no-self-use,no-member
class TimeIntervalSetField(serializers.Field):
    """Representation of TimeIntervalSet."""
    default_error_messages = {
        'incorrect_type': 'Incorrect type. Expected a string or list/tuple, '
                          'but got {input_type}',
        'incorrect_format': 'Incorrect format.',
    }

    def to_representation(self, obj):
        return obj.to_json()

    def to_internal_value(self, data):
        # pylint: disable=missing-docstring
        if not isinstance(data, (string_types, list, tuple)):
            self.fail('incorrect_type', input_type=type(data).__name__)
        if not TimeIntervalSet.validate_json(data):
            self.fail('incorrect_format')

        return TimeIntervalSet.from_json(data)
