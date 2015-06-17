# coding=utf-8
from collections import deque
from six.moves import filter, range
import calendar
import datetime as dt

from tempo.utils import default


class Schedule(object):
    """Defined in terms of sets of _years, _months, _days, _hours, etc.

    With `forward` method user can iterate datetimes that belong
    to defined sets.

    Datetime objects can be tests for containment in schedule objects.
    """
    SECONDS  = list(range(0, 60))
    MINUTES  = list(range(0, 60))
    HOURS    = list(range(0, 24))
    DAYS     = list(range(1, 31 + 1))
    WEEKDAYS = list(range(1, 7 + 1))
    MONTHS   = list(range(1, 12 + 1))
    YEARS    = list(range(dt.MINYEAR, dt.MAXYEAR + 1))
    ATTRS    = ('_seconds_value', '_minutes_value', '_hours_value',
                '_days_value', '_weekdays_value', '_months_value',
                '_years_value')

    __slots__ = ATTRS

    def __init__(self, seconds=None, minutes=None, hours=None, days=None,
                 weekdays=None, months=None, years=None):
        for value, attr, possible in [
            (seconds,  '_seconds_value',  self.SECONDS),
            (minutes,  '_minutes_value',  self.MINUTES),
            (hours,    '_hours_value',    self.HOURS),
            (days,     '_days_value',     self.DAYS),
            (weekdays, '_weekdays_value', self.WEEKDAYS),
            (months,   '_months_value',   self.MONTHS),
            (years,    '_years_value',    self.YEARS)
        ]:
            if value is not None and len(value) > 0:
                assert set(value) <= set(possible)
                setattr(self, attr, sorted(value))
            else:
                setattr(self, attr, None)

    @property
    def _years(self):
        return default(self._years_value, self.YEARS)

    @property
    def _months(self):
        return default(self._months_value, self.MONTHS)

    @property
    def _days(self):
        return default(self._days_value, self.DAYS)

    @property
    def _weekdays(self):
        return default(self._weekdays_value, self.WEEKDAYS)

    @property
    def _hours(self):
        return default(self._hours_value, self.HOURS)

    @property
    def _minutes(self):
        return default(self._minutes_value, self.MINUTES)

    @property
    def _seconds(self):
        return default(self._seconds_value, self.SECONDS)

    def _iteryears(self):
        return iter(self._years)

    def _itermonths(self):
        return iter(self._months)

    def _iterdays(self, year, month):
        for day, weekday in calendar.Calendar().itermonthdays2(year, month):
            if day == 0:
                continue
            if (day in self._days or
                weekday in self._weekdays):
                yield day

    def _iterhours(self):
        return iter(self._hours)

    def _iterminutes(self):
        return iter(self._minutes)

    def _iterseconds(self):
        return iter(self._seconds)

    def __contains__(self, item):
        return (
            item.year in self._years and
            item.month in self._months and
            (item.day in self._days or item.weekday() in self._weekdays) and
            item.hour in self._hours and
            item.minute in self._minutes and
            item.second in self._seconds
        )

    @staticmethod
    def _iterate(places, stack, context):
        """Helper, that performs one step in calculation of next value
        in kind of a numerical system, that represents
        date/time. 'places' is a list of tuples `(fn(context), 'key')`.
        Each tuple represents a part of the date/time numeral system.
        Function must construct iterator over values for given context.
        And key is a key in the context which will be used to store values
        from iterator in the context.
        Context holds current values for other places. It's needed because
        one places can only be calulcated with knowledge of values of
        other places. Such as day of month - since number of days vary from
        month to month, we must know the month before calculate next day.
        """

        # TODO Maybe this should be broken down into small functions.
        try:
            iterator, key = stack[-1]
        except IndexError:
            pass
        else:
            try:
                result = next(iterator)
            except StopIteration:
                context.pop(key, None)
                stack.pop()
                return

            context[key] = result

        if len(stack) < len(places):
            fn, key = places[len(stack)]
            stack.append((fn(context), key))

    def forward(self, datetime=None):
        context = {}
        places = [
            (lambda ctx: self._iteryears(), 'year'),
            (lambda ctx: self._itermonths(), 'month'),
            (lambda ctx: self._iterdays(ctx['year'], ctx['month']), 'day'),
            (lambda ctx: self._iterhours(), 'hour'),
            (lambda ctx: self._iterminutes(), 'minute'),
            (lambda ctx: self._iterseconds(), 'second'),
        ]

        datetime = default(datetime, dt.datetime.now())
        start_places = [
            (lambda ctx: (y for y in self._iteryears() if y >= datetime.year),
             'year'),
            (lambda ctx: (m for m in self._itermonths() if m >= datetime.month)
                         if ctx['year'] == datetime.year
                         else self._itermonths(),
             'month'),
            (lambda ctx: (d for d in self._iterdays(ctx['year'], ctx['month'])
                          if d >= datetime.day)
                         if ctx['year'] == datetime.year and
                            ctx['month'] == datetime.month
                         else self._iterdays(ctx['year'], ctx['month']),
             'day'),
            (lambda ctx: (h for h in self._iterhours() if h >= datetime.hour)
                         if ctx['year'] == datetime.year and
                            ctx['month'] == datetime.month and
                            ctx['day'] == datetime.day
                         else self._iterhours(),
             'hour'),
            (lambda ctx: (m for m in self._iterminutes()
                          if m >= datetime.minute)
                         if ctx['year'] == datetime.year and
                            ctx['month'] == datetime.month and
                            ctx['day'] == datetime.day and
                            ctx['hour'] == datetime.hour
                         else self._iterminutes(),
             'minute'),
            (lambda ctx: (s for s in self._iterseconds()
                          if s >= datetime.second)
                         if ctx['year'] == datetime.year and
                            ctx['month'] == datetime.month and
                            ctx['day'] == datetime.day and
                            ctx['hour'] == datetime.hour and
                            ctx['minute'] == datetime.minute
                         else self._iterseconds(),
             'second'),
        ]

        stack = deque()

        while len(stack) < len(start_places):
            self._iterate(start_places, stack, context)

        assert len(stack) == len(start_places) == len(places)

        exhausts = 0

        while True:
            self._iterate(places, stack, context)
            if len(stack) == 0:
                exhausts += 1
                if exhausts > 0:
                    break

            try:
                yield dt.datetime(context['year'], context['month'],
                                  context['day'], context['hour'],
                                  context['minute'], context['second'])
            except KeyError:
                pass

    def to_dict(self):
        return {
            'years': self._years,
            'months': self._months,
            'days': self._days,
            'hours': self._hours,
            'minutes': self._minutes,
            'seconds': self._seconds
        }

    @classmethod
    def from_dict(cls, value):
        return cls(**value)
