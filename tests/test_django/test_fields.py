#!/usr/bin/env python
# coding=utf-8
import datetime as dt

import pytest

from tests.test_django.aproject.anapp.models import AModel, NullableModel
from tempo.timeintervalset import TimeIntervalSet


@pytest.mark.django_db
@pytest.mark.usefixtures('django_postgresql_tempo')
@pytest.mark.parametrize('expression, datetime, expected', [
    (["OR", [1, 15, "day", "month"]], dt.datetime(2000, 1, 10), True),
    (["OR", [1, 15, "day", "month"]], dt.datetime(2000, 1, 30), False),
])
def test_contains(expression, datetime, expected):
    """'contains' lookup."""
    timeintervalset = TimeIntervalSet.from_json(expression)
    expected_object = AModel.objects.create(schedule=timeintervalset)

    objects = AModel.objects.filter(schedule__contains=datetime)

    assert (len(objects) == 1) == expected

    if not expected:
      return

    assert objects[0] == expected_object


@pytest.mark.django_db
@pytest.mark.usefixtures('django_postgresql_tempo')
def test_null():
    """null=true option for the field works as expected."""
    NullableModel.objects.create()

    actual = NullableModel.objects.get()

    assert actual.schedule is None
