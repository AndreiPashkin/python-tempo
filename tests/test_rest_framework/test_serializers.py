# coding=utf-8
from rest_framework import serializers

from tempo.rest_framework.serializers import RecurrentEventSetField
from tempo.recurrenteventset import RecurrentEventSet


class ASerializer(serializers.Serializer):
    schedule = RecurrentEventSetField()

class AnObject:
    def __init__(self, schedule):
        self.schedule = schedule


def test_serialize():
    recurrenteventset = RecurrentEventSet.from_json(
        ['AND', [1, 10, 'day', 'month']]
    )
    obj = AnObject(recurrenteventset)

    serializer = ASerializer(obj)

    expected = {'schedule': recurrenteventset.to_json()}
    actual = serializer.data

    assert actual == expected


def test_deserialize():
    expected = recurrenteventset = RecurrentEventSet.from_json(
        ['AND', [1, 10, 'day', 'month']]
    )
    serializer = ASerializer(data={'schedule': recurrenteventset.to_json()})

    assert serializer.is_valid()
    actual = serializer.validated_data['schedule']

    assert actual == expected
