#!/usr/bin/env python
# coding=utf-8
from datetime import datetime

import pytest
from tempo.timeutils import add_delta

from tempo.unit import Unit, MAX, MIN


@pytest.mark.parametrize('datetime, delta, unit, expected', [
    # Seconds
    (datetime(2015, 1, 1), 5, Unit.SECOND, datetime(2015, 1, 1, 0, 0, 5)),
    (datetime(2015, 1, 1, 0, 0, 5), -5, Unit.SECOND, datetime(2015, 1, 1)),
    # Minutes
    (datetime(2015, 1, 1), 5, Unit.MINUTE, datetime(2015, 1, 1, 0, 5, 0)),
    (datetime(2015, 1, 1, 0, 5, 0), -5, Unit.MINUTE, datetime(2015, 1, 1)),
    # Hours
    (datetime(2015, 1, 1), 5, Unit.HOUR, datetime(2015, 1, 1, 5, 0, 0)),
    (datetime(2015, 1, 1, 5, 0, 0), -5, Unit.HOUR, datetime(2015, 1, 1)),
    # Days
    (datetime(2015, 1, 1), 5, Unit.DAY, datetime(2015, 1, 6)),
    (datetime(2015, 1, 6), -5, Unit.DAY, datetime(2015, 1, 1)),
    # Weeks
    (datetime(2015, 1, 1), 5, Unit.WEEK, datetime(2015, 2, 5)),
    (datetime(2015, 2, 5), -5, Unit.WEEK, datetime(2015, 1, 1)),
    # Months
    (datetime(2015, 1, 1), 5, Unit.MONTH, datetime(2015, 6, 1)),
    (datetime(2015, 6, 1), -5, Unit.MONTH, datetime(2015, 1, 1)),
    # Years
    (datetime(2015, 1, 1), 5, Unit.YEAR, datetime(2020, 1, 1)),
    (datetime(2020, 1, 1), -5, Unit.YEAR, datetime(2015, 1, 1)),
])
def test_add_delta(datetime, delta, unit, expected):
    """Cases for `add_delta`."""
    assert add_delta(datetime, delta, unit) == expected


@pytest.mark.parametrize('unit', [
    Unit.SECOND, Unit.MINUTE, Unit.HOUR, Unit.DAY, Unit.WEEK,
    Unit.DAY, Unit.MONTH, Unit.YEAR
])
def test_add_delta_raises_overflow_exception(unit):
    """'add_delta' raises `OverflowError` in case if resulting
    datetime is greater than `tempo.unit.MAX` or
    lesser than `tempo.unit.MIN`"""
    with pytest.raises(OverflowError):
        add_delta(MAX, 1, unit)

    with pytest.raises(OverflowError):
        add_delta(MIN, -1, unit)


def test_add_delta_raises_value_error_on_wrong_unit():
    with pytest.raises(ValueError):
        add_delta(MIN, -1, 'wrong_unit')
