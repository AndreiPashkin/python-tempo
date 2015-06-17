# coding=utf-8
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
