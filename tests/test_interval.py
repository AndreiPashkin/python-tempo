#!/usr/bin/env python
# coding=utf-8
from decimal import Decimal

import pytest

from tempo.interval import Interval


@pytest.mark.parametrize('start, stop, expected', [
    (0, 10, range(11)),
    (Decimal('0.1'), Decimal('5.1'), [Decimal('0.1'), Decimal('1.1'),
                                      Decimal('2.1'), Decimal('3.1'),
                                      Decimal('4.1'), Decimal('5.1')])
])
def test_iteration(start, stop, expected):
    """Iteration over values."""
    assert list(Interval(start, stop)) == list(expected)


@pytest.mark.parametrize('interval, item, expected', [
    (Interval(10), 5, True),
    (Interval(10), 11, False),
    (Interval(0, 10), 5, True),
    (Interval(0, 10), 15, False),
    (Interval(Decimal('0.1'), Decimal('5.1')), Decimal('3.1'), True),
    (Interval(Decimal('0.1'), Decimal('5.1')), Decimal('6.1'), False),
])
def test_containment(interval, item, expected):
    """Containment test."""
    assert (item in interval) == expected


@pytest.mark.parametrize('first, second, expected', [
    (Interval(10), Interval(10), True),
    (Interval(1, 15), Interval(1, 15), True),
    (Interval(1.5, 15.5), Interval(1.5, 15.5), True),
    (Interval(10), Interval(15), False),
    (Interval(1, 15), Interval(1, 25), False),
    (Interval(1.5, 15.5), Interval(1.5, 25.5), False),
])
def test_eq_hash(first, second, expected):
    """Cases for equality test and hashing."""
    assert (first == second) == expected

    if expected:
        assert hash(first) == hash(second)
