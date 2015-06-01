#!/usr/bin/env python
# coding=utf-8
import random as rnd
from itertools import islice

from six.moves import range

from tempo.scheduleset import ScheduleSet
from tempo.schedule import Schedule
from tests.utils import schedule_kwargs


def test_forward_random():
    """Various asserts on randomly composed schedule sets,
    such as:

        - Next datetimes are greater than previous.
        - Datetimes are "contained" in included schedules
          and "not contained" in excluded schedules.
    """
    for _ in range(10):
        schedule_set = ScheduleSet(
            [Schedule(**schedule_kwargs())
             for _ in range(rnd.randrange(1, 5))],
            [Schedule(**schedule_kwargs())
             for _ in range(rnd.randrange(1, 5))],
        )
        actual = islice(schedule_set.forward(schedule_set.min), 10)

        prev = None
        for datetime in actual:
            if prev is not None:
                assert datetime > prev
            prev = datetime
            assert any([datetime in i for i in schedule_set.include])
            assert any([datetime not in e for e in schedule_set.exclude])
