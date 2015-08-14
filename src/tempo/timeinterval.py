# coding=utf-8
"""Provides TimeInterval class."""
import datetime as dt
import json

from tempo.interval import Interval, EmptyInterval
from tempo.timeutils import delta, floor, add_delta
from tempo.unit import Unit, ORDER, MIN, BASE  # pylint: disable=unused-import


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

    def __init__(self, interval, unit, recurrence=None):
        if recurrence is not None:
            assert ORDER[unit] < ORDER[recurrence], (
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
        if isinstance(item, dt.datetime):
            item = (item,)
        elif isinstance(item, (tuple, list)):
            assert len(item) == 2
        elif isinstance(item, Interval):
            item = (item.start, item.stop)
        elif isinstance(item, EmptyInterval):
            return True
        else:
            raise AssertionError

        if self.recurrence is None:
            time_in_unit = [delta(MIN, e, self.unit) for e in item]
        else:
            time_in_unit = [delta(floor(e, self.recurrence),
                                  floor(e, self.unit), self.unit)
                            for e in item]

        # Because we need to count not only time
        # that already happened, but also time, expressed in 'unit'
        # that "happening"
        time_in_unit = [n + 1 for n in time_in_unit]

        if len(item) == 1:
            return time_in_unit[0] in self.interval
        elif len(item) == 2:
            return Interval(*time_in_unit) <= self.interval

    def __eq__(self, other):
        return (self.interval == other.interval and
                self.unit == other.unit and
                self.recurrence == other.recurrence)

    def __hash__(self):
        return hash((self.interval, self.unit, self.recurrence))

    def __str__(self):
        return ('TimeInterval({interval}, {unit}, {recurrence})'
                .format(interval=repr(self.interval), unit=repr(self.unit),
                        recurrence=repr(self.recurrence)))

    def __repr__(self):
        return self.__str__()

    def forward(self, start):
        """Iterate time intervals starting from 'start'.
        Intervals returned in form of `(start, end)` pair,
        where `start` is a datetime object representing the start
        of the interval and `end` is the non-inclusive end of the interval.

        Parameters
        ----------
        start : datetime.datetime
            A lower bound for the resulting sequence of intervals.

        Yields
        ------
        start : datetime.datetime
            Start of an interval.
        end : datetime.datetime
            End of an interval.
        """
        if self.recurrence is None:
            base = MIN
        else:
            base = floor(start, self.recurrence)

        correction = -1 * BASE[self.unit]

        def addfloor(base, n):
            """Adds 'delta' to 'base' and than floors it
            by unit of this interval."""
            return floor(add_delta(base, n, self.unit), self.unit)

        # Handle possible overlap in first interval
        try:
            first = addfloor(base, self.interval.start + correction)
            second = addfloor(base, self.interval.stop + correction + 1)
            if first < start < second:
                yield Interval(start, second)
            elif start <= first:
                yield Interval(first, second)
        except OverflowError:
            return

        if self.recurrence is None:
            return
        while True:  # Handle recurring intervals
            base = add_delta(base, 1, self.recurrence)
            try:
                first = addfloor(base, self.interval.start + correction)
                second = addfloor(base, self.interval.stop + correction + 1)
                if base > first:  # In case if flooring by week resulted
                    first = base  # as a time earlier than 'base'
                yield Interval(first, second)
            except OverflowError:
                return

    def to_json(self):
        """Exports `TimeInterval` instance to JSON serializable
        representation."""
        return [[self.interval.start, self.interval.stop],
                self.unit, self.recurrence]

    @classmethod
    def from_json(cls, value):
        """Constructs `TimeInterval` instance from JSON serializable
        representation or from JSON string."""
        if not isinstance(value, (list, tuple)):
            value = json.loads(value)

        return cls(Interval(*value[0]), *value[1:])
