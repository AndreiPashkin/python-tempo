# coding=utf-8
from six.moves import filter
import calendar
import datetime as dt

from tempo.utils import default


class Schedule(object):
    """Defined in terms of sets of _years, _months, _days, _hours, etc.

    With `forward` method user can iterate datetimes that belong
    to defined sets.

    Datetime objects can be tests for containment in schedule objects.
    """
    SECONDS  = range(0, 60)
    MINUTES  = range(0, 60)
    HOURS    = range(0, 24)
    DAYS     = range(1, 31 + 1)
    WEEKDAYS = range(1, 7 + 1)
    MONTHS   = range(1, 12 + 1)
    YEARS    = range(dt.MINYEAR, dt.MAXYEAR + 1)
    ATTRS    = ('_seconds', '_minutes', '_hours', '_days', '_weekdays',
                '_months', '_years')

    __slots__ = ATTRS

    def __init__(self, seconds=None, minutes=None, hours=None, days=None,
                 weekdays=None, months=None, years=None):
        for value, attr, possible in [(seconds, '_seconds', self.SECONDS),
                                      (minutes, '_minutes', self.MINUTES),
                                      (hours, '_hours', self.HOURS),
                                      (days, '_days', self.DAYS),
                                      (weekdays, '_weekdays', self.WEEKDAYS),
                                      (months, '_months', self.MONTHS),
                                      (years, '_years', self.YEARS)]:
            if value is not None and len(value) > 0:
                assert set(value) <= set(possible)
                setattr(self, attr, sorted(value))
            else:
                setattr(self, attr, None)

    def _iteryears(self):
        return iter(default(self._years, self.YEARS))

    def _itermonths(self):
        return iter(default(self._months, self.MONTHS))

    def _iterdays(self, year, month):
        for day, weekday in calendar.Calendar().itermonthdays2(year, month):
            if (day in default(self._days, self.DAYS) and
                weekday in default(self._weekdays, self.WEEKDAYS)):
                yield day

    def _iterhours(self):
        return iter(default(self._hours, self.HOURS))

    def _iterminutes(self):
        return iter(default(self._minutes, self.MINUTES))

    def _iterseconds(self):
        return iter(default(self._seconds, self.SECONDS))

    def __contains__(self, item):
        return (
            item.year in default(self._years, self.YEARS) and
            item.month in default(self._months, self.MONTHS) and
            item.day in default(self._days, self.DAYS) and
            item.hour in default(self._hours, self.HOURS) and
            item.minute in default(self._minutes, self.MINUTES) and
            item.second in default(self._seconds, self.SECONDS)
        )

    def forward(self, datetime=None):
        datetime = default(datetime, dt.datetime.now())

        for year in filter(lambda y: y >= datetime.year, self._iteryears()):
            for month in (filter(lambda m: m >= datetime.month,
                                 self._itermonths())
                          if year == datetime.year else self._itermonths()):
                for day in (filter(lambda d: d >= datetime.day,
                                   self._iterdays(year, month))
                            if year == datetime.year and
                               month == datetime.month
                            else self._iterdays(year, month)):
                    for hour in (filter(lambda h: h >= datetime.hour,
                                        self._iterhours())
                                 if year == datetime.year and
                                    month == datetime.month and
                                    day == datetime.day
                                 else self._iterhours()):
                        for minute in (filter(lambda m: m >= datetime.minute,
                                              self._iterminutes())
                                       if year == datetime.year and
                                          month == datetime.month and
                                          day == datetime.day and
                                          hour == datetime.hour
                                       else self._iterminutes()):
                            for second in (filter(lambda s: s >=
                                                  datetime.second,
                                           self._iterseconds())
                                           if year == datetime.year and
                                              month == datetime.month and
                                              day == datetime.day and
                                              hour == datetime.hour and
                                              minute == datetime.minute
                                           else self._iterseconds()):

                                yield dt.datetime(year=year, month=month,
                                                  day=day, hour=hour,
                                                  minute=minute, second=second)

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
