#!/usr/bin/env python
# coding=utf-8
import datetime as dt

import pytest
from tempo.django.fields import ScheduleSetField
from tests.test_django.aproject.anapp.models import AModel
from tempo.schedule import Schedule
from tempo.scheduleset import ScheduleSet


@pytest.mark.django_db
def test_contains():
    """'contains' lookup."""
    scheduleset = ScheduleSet(
        include=[Schedule(years=[2014])]
    )
    AModel.objects.create(schedule=scheduleset)
    AModel.objects.create(schedule=ScheduleSet(
        include=[Schedule(years=[2015])]
    ))
    assert (AModel.objects.filter(schedule__contains=dt.datetime(2014, 1, 1))
                          .count() ==
            1)

    obj = AModel.objects.get(schedule__contains=dt.datetime(2014, 1, 1))

    actual = ScheduleSetField.schedulset_to_dict(obj.schedule)
    expected = ScheduleSetField.schedulset_to_dict(scheduleset)

    assert actual == expected
