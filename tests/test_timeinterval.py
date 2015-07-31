#!/usr/bin/env python
# coding=utf-8
import random as rnd
from datetime import datetime as dt
from itertools import islice, chain

import pytest
from six.moves import range

from tempo.interval import Interval
from tempo.timeinterval import Unit as U, TimeInterval
from tempo.timeutils import add_delta, delta, floor
from tempo.unit import MIN, MAX, BASE

from tests.utils import randuniq, CASES


@pytest.mark.parametrize('unit, recurrence, interval, datetime, expected', [
  # ----                           Positive                            ---- #
  # Year
  (U.YEAR,   None,     (1975, 1975),     dt(1975, 1, 1, 0, 0, 0),      True),
  (U.MONTH,  U.YEAR,   (5, 5),           dt(2000, 5, 1, 0, 0, 0),      True),
  (U.WEEK,   U.YEAR,   (2, 2),           dt(2000, 1, 5, 0, 0, 0),      True),
  (U.DAY,    U.YEAR,   (5, 5),           dt(2000, 1, 5, 0, 0, 0),      True),
  (U.HOUR,   U.YEAR,   (30, 30),         dt(2000, 1, 2, 5, 0, 0),      True),
  (U.MINUTE, U.YEAR,   (66, 66),         dt(2000, 1, 1, 1, 5, 0),      True),
  (U.SECOND, U.YEAR,   (71, 71),         dt(2000, 1, 1, 0, 1, 10),     True),
  # Month
  (U.MONTH,  None,     (15, 15),         dt(2, 3, 1, 0, 0, 0),         True),
  (U.WEEK,   U.MONTH,  (2, 2),           dt(1970, 1, 5, 0, 0, 0),      True),
  (U.DAY,    U.MONTH,  (5, 5),           dt(1970, 5, 5, 0, 0, 0),      True),
  (U.HOUR,   U.MONTH,  (102, 102),       dt(1970, 1, 5, 5, 0, 0),      True),
  (U.MINUTE, U.MONTH,  (66, 66),         dt(1970, 1, 1, 1, 5, 0),      True),
  (U.SECOND, U.MONTH,  (86476, 86476),   dt(1970, 1, 2, 0, 1, 15),     True),
  # Week
  (U.WEEK,   None,     (2, 2),           dt(1, 1, 8, 0, 0),            True),
  (U.DAY,    U.WEEK,   (4, 4),           dt(2000, 5, 4, 0, 0, 0),      True),
  (U.HOUR,   U.WEEK,   (78, 78),         dt(2000, 5, 4, 5, 0, 0),      True),
  (U.MINUTE, U.WEEK,   (7326, 7326),     dt(2000, 5, 6, 2, 5, 0),      True),
  (U.SECOND, U.WEEK,   (90006, 90006),   dt(2000, 5, 2, 1, 0, 5),      True),
  # Day
  (U.DAY,    None,     (730242, 730242), dt(2000, 5, 2, 1, 0, 5),      True),
  (U.HOUR,   U.DAY,    (21, 21),         dt(2000, 8, 5, 20, 8, 5),     True),
  (U.MINUTE, U.DAY,    (66, 66),         dt(2000, 5, 5, 1, 5, 5),      True),
  (U.SECOND, U.DAY,    (3906, 3906),     dt(2000, 5, 2, 1, 5, 5),      True),
  # Hour
  (U.HOUR,   None,     (35390, 35390),   dt(5, 1, 14, 13, 0),          True),
  (U.MINUTE, U.HOUR,   (16, 16),         dt(1970, 1, 5, 5, 15, 3),     True),
  (U.SECOND, U.HOUR,   (906, 906),       dt(1970, 1, 5, 5, 15, 5),     True),
  # Minute
  (U.MINUTE, None,     (525906, 525906), dt(2, 1, 1, 5, 5),            True),
  (U.SECOND, U.MINUTE, (6, 6),           dt(1970, 1, 1, 1, 5, 5),      True),
  # Second
  (U.SECOND, None,     (104701, 104701), dt(1, 1, 2, 5, 5),            True),
  # ----                          Negative                             ---- #
  # Year
  (U.YEAR,   None,     (1975, 1975),     dt(2014, 12, 10, 20, 39, 42), False),
  (U.MONTH,  U.YEAR,   (2, 2),           dt(2004, 5, 13, 18, 17, 24),  False),
  (U.WEEK,   U.YEAR,   (3, 3),           dt(1991, 12, 2, 1, 47, 55),   False),
  (U.DAY,    U.YEAR,   (10, 10),         dt(1988, 2, 20, 21, 53, 56),  False),
  (U.HOUR,   U.YEAR,   (95, 95),         dt(1978, 9, 3, 17, 24, 15),   False),
  (U.MINUTE, U.YEAR,   (99, 99),         dt(1999, 7, 9, 4, 29, 20),    False),
  (U.SECOND, U.YEAR,   (30, 30),         dt(2000, 2, 26, 1, 42, 7),    False),
  # Month
  (U.MONTH,  None,     (70, 70),         dt(1984, 11, 23, 5, 48, 59),  False),
  (U.WEEK,   U.MONTH,  (4, 4),           dt(1990, 6, 2, 1, 32, 43),    False),
  (U.DAY,    U.MONTH,  (15, 15),         dt(1973, 6, 10, 2, 37, 7),    False),
  (U.HOUR,   U.MONTH,  (100, 100),       dt(1995, 7, 25, 14, 19, 11),  False),
  (U.MINUTE, U.MONTH,  (65, 65),         dt(2009, 12, 16, 20, 15, 31), False),
  (U.SECOND, U.MONTH,  (75, 75),         dt(2011, 3, 25, 18, 37, 40),  False),
  # Week
  (U.WEEK,   None,     (15, 15),         dt(2005, 12, 25, 10, 26, 37), False),
  (U.DAY,    U.WEEK,   (5, 5),           dt(1995, 3, 23, 12, 5, 45),   False),
  (U.HOUR,   U.WEEK,   (10, 10),         dt(1976, 12, 5, 0, 41, 20),   False),
  (U.MINUTE, U.WEEK,   (90, 90),         dt(2000, 9, 2, 7, 6, 9),      False),
  (U.SECOND, U.WEEK,   (150, 150),       dt(1981, 7, 31, 10, 55, 43),  False),
  # Day
  (U.DAY,    None,     (10, 10),         dt(1997, 3, 31, 7, 26, 45),   False),
  (U.HOUR,   U.DAY,    (22, 22),         dt(2013, 7, 21, 1, 50, 25),   False),
  (U.MINUTE, U.DAY,    (15, 15),         dt(1980, 11, 26, 23, 23, 41), False),
  (U.SECOND, U.DAY,    (300, 300),       dt(1982, 1, 28, 16, 24, 30),  False),
  # Hour
  (U.HOUR,   None,     (800, 800),       dt(2006, 10, 17, 13, 45, 51), False),
  (U.MINUTE, U.HOUR,   (23, 23),         dt(1995, 3, 5, 17, 38, 55),   False),
  (U.SECOND, U.HOUR,   (900, 900),       dt(1993, 7, 1, 20, 1, 36),    False),
  # Minute
  (U.MINUTE, None,     (300, 300),       dt(1998, 9, 23, 9, 51, 17),   False),
  (U.SECOND, U.MINUTE, (15, 15),         dt(2010, 11, 27, 19, 51, 52), False),
  # Second
  (U.SECOND, None,     (60015, 60015),   dt(1991, 9, 15, 18, 33, 28),  False),
])
def test_containment(unit, recurrence, interval, datetime, expected):
    """Various cases of containment test."""
    timeinterval = TimeInterval(Interval(*interval), unit, recurrence)

    assert (datetime in timeinterval) == expected


@pytest.mark.parametrize('first, second, expected', [
    (TimeInterval(Interval(10), U.MINUTE, U.HOUR),
     TimeInterval(Interval(10), U.MINUTE, U.HOUR), True),
    (TimeInterval(Interval(10), U.MINUTE, U.HOUR),
     TimeInterval(Interval(10), U.MINUTE, U.YEAR), False),
])
def test_eq_hash(first, second, expected):
    """Cases for equality test and hashing."""
    assert (first == second) == expected

    if expected:
        assert hash(first) == hash(second)


@pytest.mark.parametrize('interval, unit, recurrence, start, expected', [
    # Since week and months are not "synchronous", flooring by week
    # might result a date with month earlier than in passed date.
    # And it might cause invalid (earlier) "starts" in `forward()` results.
    (Interval(1, 3), U.WEEK, U.MONTH, dt(3600, 9, 1),
     [(dt(3600, 9, 1, 0, 0), dt(3600, 9, 18, 0, 0)),
      (dt(3600, 10, 1, 0, 0), dt(3600, 10, 16, 0, 0))]),
])
def test_forward_corner_cases(interval, unit, recurrence, start, expected):
    """Corner cases for `forward()` method."""
    timeinterval = TimeInterval(interval=interval, unit=unit,
                                recurrence=recurrence)
    actual = list(islice((e for e in timeinterval.forward(start)),
                         len(expected)))

    assert actual == expected


N = 10


@pytest.mark.parametrize('unit, overlap', chain.from_iterable([
    [(unit, True), (unit, False)]
    for unit, recurrence in CASES
    if recurrence is None
] * 10))
def test_forward_non_recurrent_random(unit, overlap):
    """`forward()` method of non-recurrent time intervals with and without
    overlapping `start` date."""
    correction = BASE[unit]

    max_ = add_delta(MAX, -1 * N, unit)

    unit_maximum = delta(MIN, max_, unit)

    interval = Interval(*sorted(randuniq(2, correction, unit_maximum)))

    if overlap:
        start = add_delta(
            MIN,
            rnd.randrange(
                int(interval.start), int(interval.stop)
            ) - correction,
            unit
        )
    else:
        start = add_delta(MIN,
                          int(interval.start) - correction,
                          unit)

    stop = add_delta(MIN, int(interval.stop) - correction + 1, unit)
    expected = [(start, stop)]

    timeinterval = TimeInterval(interval, unit, None)
    actual = list(islice(timeinterval.forward(start), None, N))

    assert actual == expected


@pytest.mark.parametrize('unit, recurrence, overlap', chain.from_iterable([
    [(unit, recurrence, True), (unit, recurrence, False)]
    for unit, recurrence in CASES
    if recurrence is not None
] * 10))
def test_forward_recurrent_random(unit, recurrence, overlap):
    """`forward()` method of recurrent time intervals with and without
    overlapping `start` date."""
    correction = BASE[unit]

    max_ = add_delta(MAX, -1 * N, recurrence)

    unit_maximum = delta(MIN, add_delta(MIN, 1, recurrence), unit)

    interval = Interval(*sorted(randuniq(2, correction, unit_maximum)))

    expected = []

    initial = start = floor(
        add_delta(MIN, rnd.randrange(delta(MIN, max_, unit)), unit),
        recurrence
    )

    if overlap:
        initial = start = add_delta(
            initial,
            rnd.randrange(
                int(interval.start), int(interval.stop)
            ) - correction,
            unit
        )

    for i in range(N):
        recurrence_start = floor(start, recurrence)
        first = floor(add_delta(recurrence_start,
                                interval.start - correction,
                                unit), unit)
        second = add_delta(floor(add_delta(recurrence_start,
                                 interval.stop - correction,
                                 unit),
                            unit), 1, unit)
        assert first < second
        assert start < second
        if start > first:
            first = start

        expected.append((first, second))
        start = floor(add_delta(recurrence_start, 1, recurrence), recurrence)

    timeinterval = TimeInterval(interval, unit, recurrence)
    actual = list(islice(timeinterval.forward(initial), None, N))

    assert actual == expected
