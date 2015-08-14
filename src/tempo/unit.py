# coding=utf-8
"""Date/time related constants."""
import datetime as dt

# Minimum and maximum points of time within which
# the library is able to operate
MIN = dt.datetime(year=1, month=1, day=1)
MAX = dt.datetime(year=9999, month=12, day=31,
                  hour=23, minute=59, second=59)


# Units relations
SECONDS_IN_MINUTE   = 60
MINUTES_IN_HOUR     = 60
SECONDS_IN_HOUR     = SECONDS_IN_MINUTE * MINUTES_IN_HOUR
HOURS_IN_DAY        = 24
MINUTES_IN_DAY      = MINUTES_IN_HOUR * HOURS_IN_DAY
SECONDS_IN_DAY      = MINUTES_IN_DAY * SECONDS_IN_MINUTE
DAYS_IN_WEEK        = 7
HOURS_IN_WEEK       = HOURS_IN_DAY * DAYS_IN_WEEK
MINUTES_IN_WEEK     = HOURS_IN_WEEK * MINUTES_IN_HOUR
SECONDS_IN_WEEK     = MINUTES_IN_WEEK * SECONDS_IN_MINUTE
MONTHS_IN_YEAR      = 12
DAYS_IN_COMMON_YEAR = 365
DAYS_IN_LEAP_YEAR   = 366
DAYS_OF_COMMON_YEAR = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
DAYS_OF_LEAP_YEAR   = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


class Unit:  # pylint: disable=old-style-class,no-init
    """"Enumeration of supported time units."""
    SECOND  = 'second'
    MINUTE  = 'minute'
    HOUR    = 'hour'
    DAY     = 'day'
    WEEK    = 'week'
    MONTH   = 'month'
    YEAR    = 'year'


# Order of places in time representation
ORDER = {
    Unit.SECOND: 1,
    Unit.MINUTE: 2,
    Unit.HOUR  : 3,
    Unit.DAY   : 4,
    Unit.WEEK  : 5,
    Unit.MONTH : 6,
    Unit.YEAR  : 7
}

# Used for distinguishing zero-based and one-based units.
BASE = {
    Unit.SECOND: 0,
    Unit.MINUTE: 0,
    Unit.HOUR  : 0,
    Unit.DAY   : 1,
    Unit.WEEK  : 1,
    Unit.MONTH : 1,
    Unit.YEAR  : 1
}
