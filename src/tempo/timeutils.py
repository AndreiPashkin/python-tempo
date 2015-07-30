#!/usr/bin/env python
# coding=utf-8
import calendar
import datetime as dt
import math

from six.moves import range

from tempo.unit import (Unit, SECONDS_IN_MINUTE, SECONDS_IN_HOUR,
                        SECONDS_IN_DAY, DAYS_IN_WEEK, DAYS_OF_COMMON_YEAR,
                        DAYS_OF_LEAP_YEAR, MIN, MAX)


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


def _check_overflow(datetime, seconds=0, minutes=0, hours=0,
                    days=0):
    kwargs = {
        'seconds': seconds,
        'minutes': minutes,
        'hours': hours,
        'days': days
    }
    delta = dt.timedelta(**kwargs)
    total_seconds = delta.total_seconds()

    if (total_seconds > 0) and (datetime > (MAX - abs(delta))):
        raise OverflowError
    elif (total_seconds < 0) and (datetime < (MIN + abs(delta))):
        raise OverflowError


def add_delta(datetime, delta, unit):
    """Adds a 'delta' expressed in 'unit' to given 'datetime'.

    Parameters
    ----------
    datetime : datetime.datetime
        A datetime to which delta will be added.
    delta : int
        Delta to add.
    unit : str
        Units of delta.

    Raises
    ------
    OverflowError
        Datetime, in a result of delta addition becomes
        greater than 'tempo.unit.MAX' or lesser than 'tempo.unit.MAX'.

    ValueError
        Improper 'unit' passed.

    Returns
    -------
    datetime.datetime
        A new datetime object with added delta.

    Examples
    --------
    >>> from datetime import datetime
    >>> add_delta(datetime(2000, 10, 10), 5, Unit.DAY)
    ... datetime(2000, 10, 15, 0, 0)
    """
    if unit == Unit.SECOND:
        _check_overflow(datetime, seconds=delta)
        return datetime + dt.timedelta(seconds=delta)
    elif unit == Unit.MINUTE:
        _check_overflow(datetime, minutes=delta)
        return datetime + dt.timedelta(minutes=delta)
    elif unit == Unit.HOUR:
        _check_overflow(datetime, hours=delta)
        return datetime + dt.timedelta(hours=delta)
    elif unit == Unit.DAY:
        _check_overflow(datetime, days=delta)
        return datetime + dt.timedelta(days=delta)
    elif unit == Unit.WEEK:
        days = DAYS_IN_WEEK * delta
        _check_overflow(datetime, days=days)
        return datetime + dt.timedelta(days=days)
    elif unit == Unit.MONTH:
        days = 0
        while delta != 0:
            start, end = sorted((datetime.month,
                                 max(min(datetime.month + delta, 12), 1)))

            if calendar.isleap(datetime.year):
                DAYS_OF_YEAR = DAYS_OF_LEAP_YEAR
            else:
                DAYS_OF_YEAR = DAYS_OF_COMMON_YEAR

            days += int(math.copysign(sum(DAYS_OF_YEAR[start - 1:end - 1]),
                                      delta))
            delta -= int(math.copysign(end - start, delta))

        _check_overflow(datetime, days=days)
        return datetime + dt.timedelta(days=days)
    elif unit == Unit.YEAR:
        days = 0
        start, end = sorted((datetime.year, datetime.year + delta))
        for year in range(start, end):
            if calendar.isleap(year):
                days += sum(DAYS_OF_LEAP_YEAR)
            else:
                days += sum(DAYS_OF_COMMON_YEAR)

        days = int(math.copysign(days, delta))
        _check_overflow(datetime, days=days)
        return datetime + dt.timedelta(days=days)
    else:
        raise ValueError
