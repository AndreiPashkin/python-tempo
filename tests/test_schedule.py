#!/usr/bin/env python
# coding=utf-8
import datetime as dt
from itertools import islice

import pytest
from faker import Faker
from funclib.positional import first
from six.moves import range

from tempo.schedule import Schedule
from tests.utils import schedule_kwargs

fake = Faker()


@pytest.mark.parametrize('kwargs, datetime, expected', [
    # There was a bug when first result was with 20 hour
    # because of wrong calculation of a first date in a sequence.
    ({'years': [2000], 'months': [3], 'hours': [0, 20]},
     dt.datetime(2000, 1, 1, 5, 0, 0), [
        dt.datetime(2000, 3, 1, 0, 0, 0),
        dt.datetime(2000, 3, 1, 0, 0, 1),
        dt.datetime(2000, 3, 1, 0, 0, 2)
    ]),
])
def test_forward(kwargs, datetime, expected):
    """Corner cases of `Schedule.forward`."""
    schedule = Schedule(**kwargs)
    actual = list(islice(schedule.forward(datetime), len(expected)))
    assert actual == expected


def forward(datetime, seconds=None, minutes=None, hours=None, days=None,
            weekdays=None, months=None, years=None):
    """'Brute force' implementation of `Schedule.forward` functionality."""
    delta = dt.timedelta(seconds=1)

    seconds = sorted(seconds or Schedule.SECONDS)
    minutes = sorted(minutes or Schedule.MINUTES)
    hours = sorted(hours or Schedule.HOURS)
    days = sorted(days or Schedule.DAYS)
    weekdays = sorted(weekdays or Schedule.WEEKDAYS)
    months = sorted(months or Schedule.MONTHS)
    years = sorted(years or Schedule.YEARS)

    checks = [
        (lambda d: d.second,    set(seconds)),
        (lambda d: d.minute,    set(minutes)),
        (lambda d: d.hour,      set(hours)),
        (lambda d: d.day,       set(days)),
        (lambda d: d.weekday(), set(weekdays)),
        (lambda d: d.month,     set(months)),
        (lambda d: d.year,      set(years))
    ]
    if datetime.year not in years:
        datetime = dt.datetime(
            first((y for y in years if y >= datetime.year), datetime.year),
            1, 1
        )

    while True:
        for getter, data in checks:
            if getter(datetime) not in data:
                break
        else:
            yield datetime.replace(microsecond=0)

        try:
            datetime += delta
        except OverflowError:
            break


def test_forward_random():
    """Random comparisons between 'brute force' calculated sequences
    and `Schedule.forward` outputs."""
    for i in range(5):
        kwargs = schedule_kwargs()

        datetime = fake.date_time_between(
            dt.datetime(dt.MINYEAR, 1, 1),
            dt.datetime(min(kwargs['years']), 1, 1)
        )
        actual = list(islice(Schedule(**kwargs).forward(datetime), 10))
        expected = list(islice(forward(datetime, **kwargs), 10))

        assert actual == expected
