# coding=utf-8
import json
import random as rnd
from datetime import datetime as dt, timedelta
from itertools import islice, chain

import pytest
from six.moves import range

from tempo.recurrentevent import Unit as U, RecurrentEvent
from tempo.timeutils import add_delta, delta, floor
from tempo.unit import MIN, MAX, BASE

from tests.utils import randuniq, CASES, unit_span, guess, sample


@pytest.mark.parametrize('unit, recurrence, interval, datetime, expected', [
  # ----                           Positive                            ---- #
  # Year
  (U.YEAR,   None,     (1975, 1976),     dt(1975, 1, 1, 0, 0, 0),      True),
  (U.MONTH,  U.YEAR,   (5, 6),           dt(2000, 5, 1, 0, 0, 0),      True),
  (U.WEEK,   U.YEAR,   (2, 3),           dt(2000, 1, 5, 0, 0, 0),      True),
  (U.DAY,    U.YEAR,   (5, 6),           dt(2000, 1, 5, 0, 0, 0),      True),
  (U.HOUR,   U.YEAR,   (29, 30),         dt(2000, 1, 2, 5, 0, 0),      True),
  (U.MINUTE, U.YEAR,   (65, 66),         dt(2000, 1, 1, 1, 5, 0),      True),
  (U.SECOND, U.YEAR,   (70, 71),         dt(2000, 1, 1, 0, 1, 10),     True),
  # Month
  (U.MONTH,  None,     (15, 16),         dt(2, 3, 1, 0, 0, 0),         True),
  (U.WEEK,   U.MONTH,  (2, 3),           dt(1970, 1, 5, 0, 0, 0),      True),
  (U.DAY,    U.MONTH,  (5, 6),           dt(1970, 5, 5, 0, 0, 0),      True),
  (U.HOUR,   U.MONTH,  (101, 102),       dt(1970, 1, 5, 5, 0, 0),      True),
  (U.MINUTE, U.MONTH,  (65, 66),         dt(1970, 1, 1, 1, 5, 0),      True),
  (U.SECOND, U.MONTH,  (86475, 86476),   dt(1970, 1, 2, 0, 1, 15),     True),
  # Week
  (U.WEEK,   None,     (2, 3),           dt(1, 1, 8, 0, 0),            True),
  (U.DAY,    U.WEEK,   (4, 5),           dt(2000, 5, 4, 0, 0, 0),      True),
  (U.HOUR,   U.WEEK,   (77, 78),         dt(2000, 5, 4, 5, 0, 0),      True),
  (U.MINUTE, U.WEEK,   (7325, 7326),     dt(2000, 5, 6, 2, 5, 0),      True),
  (U.SECOND, U.WEEK,   (90005, 90006),   dt(2000, 5, 2, 1, 0, 5),      True),
  # Day
  (U.DAY,    None,     (730242, 730243), dt(2000, 5, 2, 1, 0, 5),      True),
  (U.HOUR,   U.DAY,    (20, 21),         dt(2000, 8, 5, 20, 8, 5),     True),
  (U.MINUTE, U.DAY,    (65, 66),         dt(2000, 5, 5, 1, 5, 5),      True),
  (U.SECOND, U.DAY,    (3905, 3906),     dt(2000, 5, 2, 1, 5, 5),      True),
  # Hour
  (U.HOUR,   None,     (35389, 35390),   dt(5, 1, 14, 13),             True),
  (U.MINUTE, U.HOUR,   (15, 16),         dt(1970, 1, 5, 5, 15, 3),     True),
  (U.SECOND, U.HOUR,   (905, 906),       dt(1970, 1, 5, 5, 15, 5),     True),
  # Minute
  (U.MINUTE, None,     (525905, 525906), dt(2, 1, 1, 5, 5),            True),
  (U.SECOND, U.MINUTE, (5, 6),           dt(1970, 1, 1, 1, 5, 5),      True),
  # Second
  (U.SECOND, None,     (104700, 104701), dt(1, 1, 2, 5, 5),            True),
  # ----                          Negative                             ---- #
  # Year
  (U.YEAR,   None,     (1975, 1976),     dt(2014, 12, 10, 20, 39, 42), False),
  (U.MONTH,  U.YEAR,   (2, 3),           dt(2004, 5, 13, 18, 17, 24),  False),
  (U.WEEK,   U.YEAR,   (3, 4),           dt(1991, 12, 2, 1, 47, 55),   False),
  (U.DAY,    U.YEAR,   (10, 11),         dt(1988, 2, 20, 21, 53, 56),  False),
  (U.HOUR,   U.YEAR,   (95, 96),         dt(1978, 9, 3, 17, 24, 15),   False),
  (U.MINUTE, U.YEAR,   (99, 100),        dt(1999, 7, 9, 4, 29, 20),    False),
  (U.SECOND, U.YEAR,   (30, 31),         dt(2000, 2, 26, 1, 42, 7),    False),
  # Month
  (U.MONTH,  None,     (70, 71),         dt(1984, 11, 23, 5, 48, 59),  False),
  (U.WEEK,   U.MONTH,  (4, 5),           dt(1990, 6, 2, 1, 32, 43),    False),
  (U.DAY,    U.MONTH,  (15, 16),         dt(1973, 6, 10, 2, 37, 7),    False),
  (U.HOUR,   U.MONTH,  (100, 101),       dt(1995, 7, 25, 14, 19, 11),  False),
  (U.MINUTE, U.MONTH,  (65, 66),         dt(2009, 12, 16, 20, 15, 31), False),
  (U.SECOND, U.MONTH,  (75, 76),         dt(2011, 3, 25, 18, 37, 40),  False),
  # Week
  (U.WEEK,   None,     (15, 16),         dt(2005, 12, 25, 10, 26, 37), False),
  (U.DAY,    U.WEEK,   (5, 6),           dt(1995, 3, 23, 12, 5, 45),   False),
  (U.HOUR,   U.WEEK,   (10, 11),         dt(1976, 12, 5, 0, 41, 20),   False),
  (U.MINUTE, U.WEEK,   (90, 91),         dt(2000, 9, 2, 7, 6, 9),      False),
  (U.SECOND, U.WEEK,   (150, 151),       dt(1981, 7, 31, 10, 55, 43),  False),
  # Day
  (U.DAY,    None,     (10, 11),         dt(1997, 3, 31, 7, 26, 45),   False),
  (U.HOUR,   U.DAY,    (22, 23),         dt(2013, 7, 21, 1, 50, 25),   False),
  (U.MINUTE, U.DAY,    (15, 16),         dt(1980, 11, 26, 23, 23, 41), False),
  (U.SECOND, U.DAY,    (300, 301),       dt(1982, 1, 28, 16, 24, 30),  False),
  # Hour
  (U.HOUR,   None,     (800, 801),       dt(2006, 10, 17, 13, 45, 51), False),
  (U.MINUTE, U.HOUR,   (23, 24),         dt(1995, 3, 5, 17, 38, 55),   False),
  (U.SECOND, U.HOUR,   (900, 901),       dt(1993, 7, 1, 20, 1, 36),    False),
  # Minute
  (U.MINUTE, None,     (300, 301),       dt(1998, 9, 23, 9, 51, 17),   False),
  (U.SECOND, U.MINUTE, (15, 16),         dt(2010, 11, 27, 19, 51, 52), False),
  # Second
  (U.SECOND, None,     (60015, 60016),   dt(1991, 9, 15, 18, 33, 28),  False),
  # Empty case
  (U.SECOND, U.MINUTE, (5, 5),           dt(1991, 1, 1, 1, 1, 5),      False),
  # Case where interval stop equals to 'unit' component
  (U.MONTH,  U.YEAR,   (4, 5),           dt(2005, 5, 15),              False)
])
def test_containment(unit, recurrence, interval, datetime, expected):
    """Various cases of containment test."""
    recurrentevent = RecurrentEvent(interval[0], interval[1], unit, recurrence)

    assert (datetime in recurrentevent) == expected


@pytest.mark.parametrize('first, second, expected', [
    (RecurrentEvent(0, 10, U.MINUTE, U.HOUR),
     RecurrentEvent(0, 10, U.MINUTE, U.HOUR), True),
    (RecurrentEvent(0, 10, U.MINUTE, U.HOUR),
     RecurrentEvent(0, 10, U.MINUTE, U.YEAR), False),
])
def test_eq_hash(first, second, expected):
    """Cases for equality test and hashing."""
    assert (first == second) == expected

    if expected:
        assert hash(first) == hash(second)


def test_eq_with_other_type():
    """Equality for object with othery type should not throw exceptions
    and return False."""
    recurrentevent = RecurrentEvent(0, 10, U.MINUTE, U.HOUR)
    other = object()

    assert not (recurrentevent == other)


@pytest.mark.parametrize('interval, unit, recurrence, start, trim, expected', [
    # Since week and months are not "synchronous", flooring by week
    # might result a date with month earlier than in passed date.
    # And it might cause invalid (earlier) "starts" in `forward()` results.
    ((1, 3), U.WEEK, U.MONTH, dt(3600, 9, 1), True,
     [(dt(3600, 9, 1, 0, 0), dt(3600, 9, 11, 0, 0)),
      (dt(3600, 10, 1, 0, 0), dt(3600, 10, 9, 0, 0))]),
    # Cases, when intervals values overflows maximum values of time component.
    # In that cases it is expected, that results will be clamped by maximum
    # time component value.
    ((1, 35), U.DAY, U.MONTH, dt(2000, 1, 1), True,
     [(dt(2000, 1, 1), dt(2000, 2, 1)),
      (dt(2000, 2, 1), dt(2000, 3, 1))]),
    # Non-inclusive end with one-based units
    ((1, 6), U.WEEK, U.MONTH, dt(2000, 1, 1), True,
     [(dt(2000, 1, 1), dt(2000, 1, 31)),
      (dt(2000, 2, 1), dt(2000, 3, 1))]),
    ((1, 20), U.DAY, U.MONTH, dt(2000, 1, 1), True,
     [(dt(2000, 1, 1), dt(2000, 1, 20))]),
    # Case of gapless interval
    ((0, 60), U.SECOND, U.MINUTE, dt(2000, 1, 1), True,
     [(dt(2000, 1, 1), MAX)]),
    ((0, 60), U.SECOND, U.MINUTE, dt(2000, 1, 1), True,
     [(dt(2000, 1, 1), MAX)]),
    # trim=False
    ((10, 20), U.DAY, U.MONTH, dt(2000, 1, 15), False,
     [(dt(2000, 1, 10), dt(2000, 1, 20))])
])
def test_forward_corner_cases(interval, unit, recurrence, start, trim,
                              expected):
    """Corner cases for `forward()` method."""
    recurrentevent = RecurrentEvent(start=interval[0], stop=interval[1],
                                unit=unit, recurrence=recurrence)
    actual = list(islice((e for e in recurrentevent.forward(start, trim)),
                         len(expected)))

    assert actual == expected


N = 10

# TODO Refactor using fixtures
@pytest.mark.parametrize('unit, overlap, trim', chain.from_iterable([
    [(unit, True, False), (unit, False, False),
     (unit, True, True), (unit, False, True)]
    for unit, recurrence in CASES
    if recurrence is None
] * 10))
def test_forward_non_recurrent_random(unit, overlap, trim):
    """`forward()` method of non-recurrent time intervals with and without
    overlapping `start` date."""
    correction = BASE[unit]

    max_ = add_delta(MAX, -1 * N, unit)

    unit_maximum = delta(MIN, max_, unit)

    interval = sorted(randuniq(2, correction, unit_maximum))

    if overlap:
        start = add_delta(
            MIN,
            rnd.randrange(int(interval[0]), int(interval[1])) - correction,
            unit
        )
    else:
        start = add_delta(MIN, int(interval[0]) - correction, unit)

    if trim:
        expected_start = start
    else:
        expected_start = add_delta(MIN, int(interval[0]) - correction, unit)

    stop = add_delta(MIN, int(interval[1]) - correction, unit)

    expected = [(expected_start, stop)]

    recurrentevent = RecurrentEvent(interval[0], interval[1], unit, None)
    actual = list(islice(recurrentevent.forward(start, trim), None, N))

    assert actual == expected


@pytest.mark.parametrize('unit, recurrence, overlap, trim',
chain.from_iterable([
    [(unit, recurrence, True, False), (unit, recurrence, False, False),
     (unit, recurrence, True, True), (unit, recurrence, False, True)]
    for unit, recurrence in CASES
    if recurrence is not None
] * 10))
def test_forward_recurrent_random(unit, recurrence, overlap, trim):
    """`forward()` method of recurrent time intervals with and without
    overlapping `start` date."""
    correction = BASE[unit]

    max_ = add_delta(MAX, -1 * N, recurrence)

    unit_maximum = delta(MIN, add_delta(MIN, 1, recurrence), unit)

    from_, to = sorted(randuniq(2, correction, unit_maximum))

    expected = []

    initial = start = floor(
        add_delta(MIN, rnd.randrange(delta(MIN, max_, unit)), unit),
        recurrence

    )

    if overlap:
        initial = start = add_delta(
            initial,
            rnd.randrange(
                int(from_), int(to)
            ) - correction,
            unit
        )

    for i in range(N):
        recurrence_start = floor(start, recurrence)
        recurrence_stop = floor(add_delta(recurrence_start, 1, recurrence),
                                recurrence)
        first = floor(add_delta(recurrence_start,
                                from_ - correction,
                                unit), unit)
        second = floor(add_delta(recurrence_start, to - correction, unit),
                       unit)
        first = max(recurrence_start, min(first, recurrence_stop))
        second = min(recurrence_stop, second)
        assert first <= second
        assert start <= second
        if start > first and trim:
            first = start

        expected.append((first, second))
        start = floor(add_delta(recurrence_start, 1, recurrence), recurrence)

    recurrentevent = RecurrentEvent(from_, to, unit, recurrence)
    actual = list(islice(recurrentevent.forward(initial, trim), None, N))

    assert actual == expected


@pytest.mark.parametrize('interval, unit, recurrence, expected', [
    ((1, 15), U.YEAR, None, [1, 15, 'year', None]),
    ((0, 12), U.MONTH, U.YEAR, [0, 12, 'month', 'year'])
])
def test_to_json(interval, unit, recurrence, expected):
    """Cases for `to_json()` method."""
    actual = RecurrentEvent(interval[0], interval[1], unit, recurrence).to_json()

    assert actual == expected


@pytest.mark.parametrize('value, expected', [
    (json.dumps([1, 15, 'year', None]),
     RecurrentEvent(1, 15, U.YEAR, None)),
    (json.dumps([1, 15, 'month', 'year']),
     RecurrentEvent(1, 15, U.MONTH, U.YEAR)),
    ([1, 15, 'month', 'year'],
     RecurrentEvent(1, 15, U.MONTH, U.YEAR)),
])
def test_from_json(value, expected):
    """Cases for `from_json()` method."""
    actual = RecurrentEvent.from_json(value)

    assert actual == expected
