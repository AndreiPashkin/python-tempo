#!/usr/bin/env python
# coding=utf-8
import datetime as dt


SECONDS_IN_MINUTE = 60
MINUTES_IN_HOUR = 60
SECONDS_IN_HOUR = SECONDS_IN_MINUTE * MINUTES_IN_HOUR
HOURS_IN_DAY = 24
MINUTES_IN_DAY = MINUTES_IN_HOUR * HOURS_IN_DAY
SECONDS_IN_DAY = MINUTES_IN_DAY * SECONDS_IN_MINUTE
DAYS_IN_WEEK = 7
HOURS_IN_WEEK = HOURS_IN_DAY * DAYS_IN_WEEK
MINUTES_IN_WEEK = HOURS_IN_WEEK * MINUTES_IN_HOUR
SECONDS_IN_WEEK = MINUTES_IN_WEEK * SECONDS_IN_MINUTE
MONTHS_IN_YEAR = 12


class Unit:
    """"Enumeration of supported time units."""
    SECOND  = 'second'
    MINUTE  = 'minute'
    HOUR    = 'hour'
    DAY     = 'day'
    WEEK    = 'week'
    MONTH   = 'month'
    YEAR    = 'year'


# Order of places in time representation
UNIT_ORDER = {
    Unit.SECOND: 1,
    Unit.MINUTE: 2,
    Unit.HOUR: 3,
    Unit.DAY: 4,
    Unit.WEEK: 5,
    Unit.MONTH: 6,
    Unit.YEAR: 7
}


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


class TimeInterval(object):
    """An interval of time expressed in some 'unit' of time
    (second, week, year, etc), recurring with some 'recurrence',
    also expressed in some unit of time.
    For example minutes interval can recur hourly or yearly,
    but can't recur secondly.

    With `None` passed as 'recurrence', time interval will be defined without
    recurrence, just as a single non-recurring interval between two points
    in time and counted from "the beginning of time". By convention
    "the beginning of time" is 1-1-1 00:00:00.

    Parameters
    ----------
    interval : tempo.interval.Interval
        Recurring interval of time.
    unit : str
       Unit of time in which time interval is expressed.
    recurrence : str, optional
       Recurrence of time interval. Can be (and by default is) `None`,
       which means - "no recurrence".

    Examples
    --------
    >>> from datetime import datetime
    >>> from tempo.interval import Interval
    >>> timeinterval = TimeInterval(Unit.SECOND,
    ...                             Unit.MINUTE,
    ...                             Interval(15))
    >>> datetime(2000, 1, 1, 5, 3, 10) in timeinterval
    ... True
    >>> datetime(2000, 1, 1, 5, 3, 16) in timeinterval
    ... False
    """

    MIN = dt.datetime(year=1, month=1, day=1)

    def __init__(self, interval, unit, recurrence=None):
        if recurrence is not None:
            assert UNIT_ORDER[unit] < UNIT_ORDER[recurrence], (
                '"{unit} of {recurrence}" is impossible combination.'
                .format(unit=unit, recurrence=recurrence)
            )

        self.unit = unit
        self.recurrence = recurrence
        self.interval = interval

    def __contains__(self, item):
        """Test given datetime 'item' for containment in the time interval.

        Parameters
        ----------
        item : datetime.datetime
            A 'datetime' object to test.

        Returns
        -------
        bool
            Result of containment test.

        Notes
        -----
        The algorithm here consists of following steps:

            If recurrence is set:

            1. Given datetime floored to unit of 'recurrence' and stored.
            2. Then given datetime floored to unit of 'unit' and stored.
            3. Delta between resulting datetime objects is calculated and
               expressed in units of 'unit'. For example if delta is "2 days"
               and 'unit' is minutes, delta will be "2*24*60 minutes".

            If recurrence is not set:

            1. Delta between date of "the beginning of time" and given
               date is calculated and expressed in units of 'unit'.

            4. Resulting delta tested for containment in the interval.
        """
        if self.recurrence is None:
            time_in_unit = delta(self.MIN, item, self.unit)
        else:
            time_in_unit = delta(floor(item, self.recurrence),
                                 floor(item, self.unit),
                                 self.unit)

        # Because we need to count not only time
        # that already happened, but also time, expressed in 'unit'
        # that "happening"
        time_in_unit += 1

        return time_in_unit in self.interval

    def __eq__(self, other):
        return (self.interval == other.interval and
                self.unit == other.unit and
                self.recurrence == other.recurrence)

    def __hash__(self):
        return hash((self.interval, self.unit, self.recurrence))

    def __str__(self):
        return ('TimeInterval(interval={interval}, unit={unit}, '
                'recurrence={recurrence})'
                .format(interval=repr(self.interval), unit=repr(self.unit),
                        recurrence=repr(self.recurrence)))

    def __repr__(self):
        return self.__str__()
