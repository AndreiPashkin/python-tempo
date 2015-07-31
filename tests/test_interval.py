#!/usr/bin/env python
# coding=utf-8
from decimal import Decimal

import pytest

from tempo.interval import Interval


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


@pytest.mark.parametrize('first, second, expected', [
    (Interval(1, 10), Interval(4, 6), True),
    (Interval(4, 6), Interval(1, 10), False),
    (Interval(5, 15), Interval(1, 10), False),
])
def test_gt(first, second, expected):
    """Is included test."""
    assert (first > second) == expected


@pytest.mark.parametrize('first, second, expected', [
    (Interval(1, 10), Interval(4, 6), True),
    (Interval(1, 10), Interval(1, 10), True),
    (Interval(1, 10), Interval(1, 5), True),
    (Interval(1, 10), Interval(5, 10), True),
    (Interval(4, 6), Interval(1, 10), False),
    (Interval(5, 15), Interval(1, 10), False),
])
def test_ge(first, second, expected):
    """Is included-or-equal test."""
    assert (first >= second) == expected


@pytest.mark.parametrize('first, second, expected', [
    (Interval(4, 6), Interval(1, 10), True),
    (Interval(1, 10), Interval(4, 6), False),
    (Interval(1, 10), Interval(5, 15), False),
])
def test_lt(first, second, expected):
    """Reverse included test."""
    assert (first < second) == expected


@pytest.mark.parametrize('first, second, expected', [
    (Interval(4, 6), Interval(1, 10), True),
    (Interval(4, 6), Interval(4, 6), True),
    (Interval(1, 5), Interval(1, 10), True),
    (Interval(5, 10), Interval(1, 10), True),
    (Interval(1, 10), Interval(4, 6), False),
    (Interval(1, 10), Interval(5, 15), False),
])
def test_le(first, second, expected):
    """Reverse included-or-equal test."""
    assert (first <= second) == expected
