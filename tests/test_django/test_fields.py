#!/usr/bin/env python
# coding=utf-8
import datetime as dt
from funclib.sequences import pluckattr

import pytest
from tempo.django.fields import ScheduleSetField
from tests.test_django.aproject.anapp.models import AModel, NullableModel
from tempo.schedule import Schedule
from tempo.scheduleset import ScheduleSet


@pytest.mark.parametrize('schedulesets, datetime', [
    ([ScheduleSet(include=[Schedule(years=[2014])]),
      ScheduleSet(include=[Schedule(years=[2015])])],
     dt.datetime(2014, 1, 1)),

    ([ScheduleSet(include=[Schedule(weekdays=[2], days=[15])]),
      ScheduleSet(include=[Schedule(weekdays=[4], days=[1])])],
     dt.datetime(2014, 1, 1)),

    ([ScheduleSet(include=[Schedule(seconds_of_the_day=[2], seconds=[15])]),
      ScheduleSet(include=[Schedule(seconds_of_the_day=[15], seconds=[15])])],
     dt.datetime(2014, 1, 1, 0, 0, 2))
])
@pytest.mark.django_db
def test_contains(schedulesets, datetime):
    """'contains' lookup."""
    expected = sorted(ScheduleSetField.schedulset_to_dict(s)
                      for s in schedulesets if datetime in s)
    AModel.objects.bulk_create([AModel(schedule=s) for s in schedulesets])

    objs = AModel.objects.filter(schedule__contains=datetime)

    actual = sorted(map(ScheduleSetField.schedulset_to_dict,
                        pluckattr('schedule', objs)))

    assert actual == expected


@pytest.mark.django_db
def test_null():
    """null=true option for the field works as expected."""
    NullableModel.objects.create()

    actual = NullableModel.objects.get()

    assert actual.schedule is None
