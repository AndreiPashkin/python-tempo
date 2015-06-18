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
    SECONDS_OF_THE_DAY = list(range(0, 60 * 60 * 24))
    SECONDS            = list(range(0, 60))
    MINUTES            = list(range(0, 60))
    HOURS              = list(range(0, 24))
    DAYS               = list(range(1, 31 + 1))
    WEEKDAYS           = list(range(1, 7 + 1))
    MONTHS             = list(range(1, 12 + 1))
    YEARS              = list(range(dt.MINYEAR, dt.MAXYEAR + 1))
    ATTRS              = ('seconds_of_the_day', 'seconds', 'minutes', 'hours',
                          'days', 'weekdays', 'months', 'years')

    __slots__ = ATTRS

    def __init__(self, seconds_of_the_day=None, seconds=None, minutes=None,
                 hours=None, days=None, weekdays=None, months=None,
                 years=None):
        for value, attr, possible in [
            (seconds_of_the_day, 'seconds_of_the_day',
             self.SECONDS_OF_THE_DAY),
            (seconds, 'seconds', self.SECONDS),
            (minutes, 'minutes', self.MINUTES),
            (hours, 'hours', self.HOURS),
            (days, 'days', self.DAYS),
            (weekdays, 'weekdays', self.WEEKDAYS),
            (months, 'months', self.MONTHS),
            (years, 'years', self.YEARS)
        ]:
            if value is not None and len(value) > 0:
                assert set(value) <= set(possible)
                setattr(self, attr, sorted(value))
            else:
                setattr(self, attr, None)

    @property
    def _years(self):
        return default(self.years, self.YEARS)

    @property
    def _months(self):
        return default(self.months, self.MONTHS)

    @property
    def _days(self):
        return default(self.days, self.DAYS)

    @property
    def _weekdays(self):
        return default(self.weekdays, self.WEEKDAYS)

    @property
    def _hours(self):
        return default(self.hours, self.HOURS)

    @property
    def _minutes(self):
        return default(self.minutes, self.MINUTES)

    @property
    def _seconds(self):
        return default(self.seconds, self.SECONDS)

    @property
    def _seconds_of_the_day(self):
        return default(self.seconds_of_the_day, self.SECONDS_OF_THE_DAY)

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
        return iter(sorted(
            set(self._hours) |
            {s // 60 // 60 for s in self._seconds_of_the_day}
        ))

    def _iterminutes(self, hour):
        return iter(sorted(
            (set(self._minutes)
             if hour in self._hours
             else set()) |
            {(s // 60) % 60 for s in self._seconds_of_the_day
             if (s // 60 // 60) == hour}
        ))

    def _iterseconds(self, hour, minute):
        return iter(sorted(
            (set(self._seconds)
             if hour in self._hours and minute in self._minutes
             else set()) |
            {s % 60 for s in self._seconds_of_the_day
             if s // 60 // 60 == hour and (s // 60) % 60 == minute}
        ))

    def __contains__(self, item):
        return (
            item.year in self._years and
            item.month in self._months and
            (item.day in self._days or item.weekday() in self._weekdays) and
            ((item.hour in self._hours and
              item.minute in self._minutes and
              item.second in self._seconds) or
             ((item.hour * 60 * 60 + item.minute * 60 + item.second) in
              self._seconds_of_the_day))
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

    def forward(self, start=None):
        context = {}
        places = [
            (lambda ctx: self._iteryears(), 'year'),
            (lambda ctx: self._itermonths(), 'month'),
            (lambda ctx: self._iterdays(ctx['year'], ctx['month']), 'day'),
            (lambda ctx: self._iterhours(), 'hour'),
            (lambda ctx: self._iterminutes(ctx['hour']), 'minute'),
            (lambda ctx: self._iterseconds(ctx['hour'], ctx['minute']),
             'second'),
        ]

        start = default(start, dt.datetime.now())
        start_places = [
            (lambda ctx: (y for y in self._iteryears() if y >= start.year),
             'year'),
            (lambda ctx: (m for m in self._itermonths() if m >= start.month)
                         if ctx['year'] == start.year
                         else self._itermonths(),
             'month'),
            (lambda ctx: (d for d in self._iterdays(ctx['year'], ctx['month'])
                          if d >= start.day)
                         if ctx['year'] == start.year and
                            ctx['month'] == start.month
                         else self._iterdays(ctx['year'], ctx['month']),
             'day'),
            (lambda ctx: (h for h in self._iterhours() if h >= start.hour)
                         if ctx['year'] == start.year and
                            ctx['month'] == start.month and
                            ctx['day'] == start.day
                         else self._iterhours(),
             'hour'),
            (lambda ctx: (m for m in self._iterminutes(ctx['hour'])
                          if m >= start.minute)
                         if ctx['year'] == start.year and
                            ctx['month'] == start.month and
                            ctx['day'] == start.day and
                            ctx['hour'] == start.hour
                         else self._iterminutes(ctx['hour']),
             'minute'),
            (lambda ctx: (s for s in self._iterseconds(ctx['hour'],
                                                       ctx['minute'])
                          if s >= start.second)
                         if ctx['year'] == start.year and
                            ctx['month'] == start.month and
                            ctx['day'] == start.day and
                            ctx['hour'] == start.hour and
                            ctx['minute'] == start.minute
                         else self._iterseconds(ctx['hour'], ctx['minute']),
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
