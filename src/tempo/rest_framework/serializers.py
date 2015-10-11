# coding=utf-8
"""Provides utilities for serialization/deserialization of
Tempo data types.
"""
from six import string_types

from rest_framework import serializers

from tempo.recurrenteventset import RecurrentEventSet


# pylint: disable=no-init,no-self-use,no-member
class RecurrentEventSetField(serializers.Field):
    """Representation of RecurrentEventSet."""
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
        if not RecurrentEventSet.validate_json(data):
            self.fail('incorrect_format')

        return RecurrentEventSet.from_json(data)
