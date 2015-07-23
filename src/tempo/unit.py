#!/usr/bin/env python
# coding=utf-8
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
DAYS_OF_COMMON_YEAR = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
DAYS_OF_LEAP_YEAR = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


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
