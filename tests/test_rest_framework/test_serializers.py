# coding=utf-8
from rest_framework import serializers

from tempo.rest_framework.serializers import TimeIntervalSetField
from tempo.timeintervalset import TimeIntervalSet


class ASerializer(serializers.Serializer):
    schedule = TimeIntervalSetField()

class AnObject:
    def __init__(self, schedule):
        self.schedule = schedule


def test_serialize():
    timeintervalset = TimeIntervalSet.from_json(
        ['AND', [1, 10, 'day', 'month']]
    )
    obj = AnObject(timeintervalset)

    serializer = ASerializer(obj)

    expected = {'schedule': timeintervalset.to_json()}
    actual = serializer.data

    assert actual == expected


def test_deserialize():
    expected = timeintervalset = TimeIntervalSet.from_json(
        ['AND', [1, 10, 'day', 'month']]
    )
    serializer = ASerializer(data={'schedule': timeintervalset.to_json()})

    assert serializer.is_valid()
    actual = serializer.validated_data['schedule']

    assert actual == expected
