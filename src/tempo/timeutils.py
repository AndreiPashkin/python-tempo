#!/usr/bin/env python
# coding=utf-8
import datetime as dt

from tempo.unit import (Unit, SECONDS_IN_MINUTE, SECONDS_IN_HOUR,
                        SECONDS_IN_DAY)


def _floor_by_second(datetime):
    return datetime.replace(microsecond=0)


def _floor_by_minute(datetime):
    return datetime.replace(second=0, microsecond=0)


def _floor_by_hour(datetime):
    return datetime.replace(minute=0, second=0, microsecond=0)


def _floor_by_day(datetime):
    return datetime.replace(hour=0, minute=0, second=0, microsecond=0)


def _floor_by_week(datetime):
    datetime = _floor_by_day(datetime)
    return datetime - dt.timedelta(days=datetime.weekday())


def _floor_by_month(datetime):
    return datetime.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def _floor_by_year(datetime):
    return datetime.replace(month=1, day=1, hour=0, minute=0, second=0,
                            microsecond=0)


FLOOR_FNS = {
    Unit.SECOND: _floor_by_second,
    Unit.MINUTE: _floor_by_minute,
    Unit.HOUR: _floor_by_hour,
    Unit.DAY: _floor_by_day,
    Unit.WEEK: _floor_by_week,
    Unit.MONTH: _floor_by_month,
    Unit.YEAR: _floor_by_year
}


def floor(datetime, unit):
    """Floors given datetime to closest 'unit'.

    Parameters
    ----------
    datetime : datetime.datetime
        A datetime to floor.
    unit : str
        Unit by which flooring should be performed.

    Returns
    -------
    datetime.datetime
        Floored date object.

    Examples
    --------
    >>> import datetime
    >>> floor(datetime.datetime(2014, 10, 15, 5, 15, 45), Unit.HOUR)
    ... datetime.datetime(2014, 10, 15, 5, 0, 0)

    """
    try:
        return FLOOR_FNS[unit](datetime)
    except KeyError:
        raise ValueError


def delta(datetime1, datetime2, unit):
    """Calculates time delta between two dates. Returned delta will be
    expressed in given 'unit'.

    Parameters
    ----------
    datetime1 : datetime.datetime
        First date.
    datetime2 : datetime.datetime
        Second date.
    unit : str
        Unit of delta.

    Returns
    -------
    int
        Time delta.
    """
    datetime1, datetime2 = sorted([datetime1, datetime2])

    timedelta = datetime2 - datetime1

    if unit == Unit.SECOND:
        return timedelta.total_seconds()
    elif unit == Unit.MINUTE:
        return timedelta.total_seconds() // SECONDS_IN_MINUTE
    elif unit == Unit.HOUR:
        return timedelta.total_seconds() // SECONDS_IN_HOUR
    elif unit == Unit.DAY:
        return timedelta.total_seconds() // SECONDS_IN_DAY
    elif unit == Unit.WEEK:
        return ((timedelta.total_seconds() // SECONDS_IN_DAY +
                 datetime1.weekday()) // 7)
    elif unit == Unit.MONTH:
        return (((datetime2.year - datetime1.year) * 12) -
                datetime1.month + datetime2.month)
    elif unit == Unit.YEAR:
        return datetime2.year - datetime1.year
