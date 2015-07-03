#!/usr/bin/env python
# coding=utf-8
from decimal import Decimal

import pytest

from tempo.interval import Interval


@pytest.mark.parametrize('start, stop, step, expected', [
    (0, 10, 1, range(11)),
    (0, 10, 2, range(0, 12, 2)),
    (Decimal('0.1'), Decimal('5.1'), 1, [Decimal('0.1'), Decimal('1.1'),
                                         Decimal('2.1'), Decimal('3.1'),
                                         Decimal('4.1'), Decimal('5.1')])
])
def test_iteration(start, stop, step, expected):
    """Iteration over values."""
    assert list(Interval(start, stop, step)) == list(expected)


@pytest.mark.parametrize('interval, item, expected', [
    (Interval(10), 5, True),
    (Interval(10), 11, False),
    (Interval(0, 10, 2), 6, True),
    (Interval(0, 10, 2), 7, False),
    (Interval(Decimal('0.1'), Decimal('5.1')), Decimal('3.1'), True),
    (Interval(Decimal('0.1'), Decimal('5.1')), Decimal('6.1'), False),
    (Interval(Decimal('0.1'), Decimal('5.1'), 2), Decimal('4.1'), True),
    (Interval(Decimal('0.1'), Decimal('5.1'), 2), Decimal('3.1'), False),
])
def test_containment(interval, item, expected):
    """Containment test."""
    assert (item in interval) == expected
