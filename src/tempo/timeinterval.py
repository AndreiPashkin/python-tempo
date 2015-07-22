#!/usr/bin/env python
# coding=utf-8
import datetime as dt

from tempo.timeutils import delta, floor
from tempo.unit import Unit, UNIT_ORDER


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
