# coding=utf-8
"""Provides TimeInterval class."""
import json

from tempo.timeutils import delta, floor, add_delta
# pylint: disable=unused-import
from tempo.unit import Unit, ORDER, MIN, MAX, BASE, UNITS_MAX


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
    start : int
        Start of recurring interval.
    stop : int
        Non-inclusive end of recurring interval.
    unit : str
       Unit of time in which time interval is expressed.
    recurrence : str, optional
       Recurrence of time interval. Can be (and by default is) `None`,
       which means - "no recurrence".

    Examples
    --------
    >>> from datetime import datetime
    >>> timeinterval = TimeInterval(0, 15, Unit.SECOND, Unit.MINUTE)
    >>> datetime(2000, 1, 1, 5, 3, 10) in timeinterval
    ... True
    >>> datetime(2000, 1, 1, 5, 3, 16) in timeinterval
    ... False
    """

    def __init__(self, start, stop, unit, recurrence=None):
        if recurrence is not None:
            assert ORDER[unit] < ORDER[recurrence], (
                '"{unit} of {recurrence}" is impossible combination.'
                .format(unit=unit, recurrence=recurrence)
            )

        self.unit = unit
        self.recurrence = recurrence
        self.start = start
        self.stop = stop

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
        correction = BASE[self.unit]

        if self.recurrence is None:
            time_in_unit = delta(MIN, item, self.unit)
        else:
            time_in_unit = delta(floor(item, self.recurrence),
                                 floor(item, self.unit),
                                 self.unit)

        time_in_unit += correction

        return self.start <= time_in_unit < self.stop

    def __eq__(self, other):
        return (self.start == other.start and
                self.stop == other.stop and
                self.unit == other.unit and
                self.recurrence == other.recurrence)

    def __hash__(self):
        return hash((self.start, self.stop, self.unit, self.recurrence))

    def __str__(self):
        return ('TimeInterval({start}, {stop}, {unit}, {recurrence})'
                .format(start=repr(self.start), stop=repr(self.stop),
                        unit=repr(self.unit),
                        recurrence=repr(self.recurrence)))

    def __repr__(self):
        return self.__str__()

    def _clamp_by_recurrence(self, base, *dates):
        max_ = floor(add_delta(base, 1, self.recurrence), self.recurrence)
        return [min(d, max_) for d in dates]

    def isgapless(self):
        """Tests if the TimeInterval instance defines
        infinite time interval."""
        if self.recurrence is None:
            return False

        correction = BASE[self.unit]

        return (
            (self.start - correction) == 0 and
            (self.stop - correction) == UNITS_MAX[self.unit][self.recurrence]
        )

    def forward(self, start, trim=True):
        """Iterate time intervals starting from 'start'.
        Intervals returned in form of `(start, end)` pair,
        where `start` is a datetime object representing the start
        of the interval and `end` is the non-inclusive end of the interval.

        Parameters
        ----------
        start : datetime.datetime
            A lower bound for the resulting sequence of intervals.
        trim : bool
            Whether a first interval should be trimmed by 'start' or
            it should be full, so it's start point may potentially be
            earlier, that 'start'.

        Yields
        ------
        start : datetime.datetime
            Start of an interval.
        end : datetime.datetime
            End of an interval.
        """
        # pylint: disable=too-many-branches
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
            first = addfloor(base, self.start + correction)

            if start > first:
                if trim:
                    first = start
                # If 'unit' is week, 'first' could be earlier than
                # start of 'recurrence' time component corresponding to
                # 'start'.
                elif self.recurrence is not None:
                    recurrence_start = floor(start, self.recurrence)
                    if first < recurrence_start:
                        first = recurrence_start

            if self.isgapless():
                yield first, MAX
                return

            second = addfloor(base, self.stop + correction)

            if self.recurrence is not None:
                first, second = self._clamp_by_recurrence(base, first, second)

            yield first, second
        except OverflowError:
            return

        if self.recurrence is None:
            return
        while True:  # Handle recurring intervals
            base = add_delta(base, 1, self.recurrence)
            try:
                first = addfloor(base, self.start + correction)
                second = addfloor(base, self.stop + correction)
                if base > first:  # In case if flooring by week resulted
                    first = base  # as a time earlier than 'base'

                first, second = self._clamp_by_recurrence(base, first, second)
                yield first, second
            except OverflowError:
                return

    def to_json(self):
        """Exports `TimeInterval` instance to JSON serializable
        representation."""
        return [self.start, self.stop, self.unit, self.recurrence]

    @classmethod
    def from_json(cls, value):
        """Constructs `TimeInterval` instance from JSON serializable
        representation or from JSON string."""
        if not isinstance(value, (list, tuple)):
            value = json.loads(value)

        return cls(value[0], value[1], value[2], value[3])
