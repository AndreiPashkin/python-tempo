# coding=utf-8
from datetime import datetime
import json

import pytest

from tempo.interval import Interval
from tempo.timeinterval import TimeInterval

from tempo.timeintervalset import (AND, NOT, OR, _walk, TimeIntervalSet, Void)
from tempo.unit import Unit


def callback(op, *args):
    assert all(isinstance(arg, bool) for arg in args)
    if op == AND:
        return all(args)
    elif op == OR:
        return any(args)
    elif op == NOT:
        assert len(args) == 1
        return not args[0]
    else:
        raise AssertionError


@pytest.mark.parametrize('expression, callback, expected', [
    ((AND, True, True), callback, True),
    ((AND, True, False), callback, False),
    ((OR, True, False), callback, True),
    ((OR, False, False), callback, False),
    ((NOT, False), callback, True),
    ((NOT, True), callback, False),
    ((AND, (OR, False, (NOT, False), True, (NOT, False))),
     callback, True),
    ((AND, (OR, False, (NOT, False), True, (NOT, True))),
     callback, True),
    ((AND, (NOT, True), True, (AND, False, (NOT, False))),
     callback, False),
    ((AND, (NOT, False), True, (AND, True, (NOT, False))),
     callback, True),
    ([AND, [NOT, False], True, [AND, True, [NOT, False]]],
     callback, True),
])
def test_walk(expression, callback, expected):
    """Cases for expression evaluator - '_walk' function."""
    assert _walk(expression, callback) == expected


def test_walk_raises_void():
    """If result of evaluation is empty, Void is raised."""
    expression = (OR, True, False)

    def callback(*_):
        raise Void

    with pytest.raises(Void):
        _walk(expression, callback)


@pytest.mark.parametrize('first, second, expected', [
    (TimeIntervalSet((AND,
        TimeInterval(Interval(0, 5), 'hour', 'day'),
        (NOT, TimeInterval(Interval(2, 3), 'hour', 'day'))
     )),
     TimeIntervalSet((AND,
        TimeInterval(Interval(0, 5), 'hour', 'day'),
        (NOT, TimeInterval(Interval(2, 3), 'hour', 'day'))
     )),
     True),
    (TimeIntervalSet((AND,
        TimeInterval(Interval(0, 5), 'hour', 'day'),
        (NOT, TimeInterval(Interval(2, 3), 'hour', 'day'))
     )),
     TimeIntervalSet((AND,
        TimeInterval(Interval(0, 5), 'hour', 'day'),
        (NOT, TimeInterval(Interval(2, 4), 'hour', 'day'))
     )),
     False),
])
def test_eq_hash(first, second, expected):
    """Cases for equality test and hashing."""
    assert (first == second) == expected

    if expected:
        assert hash(first) == hash(second)


@pytest.mark.parametrize('item, expression, expected', [
    (datetime(2005, 5, 15),
     (AND, TimeInterval(Interval(2, 8), 'month', 'year')),
     True),
    (datetime(2005, 12, 15),
     (AND, TimeInterval(Interval(2, 8), 'month', 'year')),
     False),
    (datetime(2005, 5, 15),
     (AND, TimeInterval(Interval(2, 8), 'month', 'year'),
            (NOT, TimeInterval(Interval(4, 5), 'month', 'year'))),
     False),
    ((datetime(2005, 4, 15), datetime(2005, 6, 15)),
     (AND, TimeInterval(Interval(2, 8), 'month', 'year')),
     True),
    ((datetime(2005, 1, 15), datetime(2005, 12, 15)),
     (AND, TimeInterval(Interval(2, 8), 'month', 'year')),
     False),
])
def test_contains(item, expression, expected):
    """Cases for containment test."""
    assert (item in TimeIntervalSet(expression)) == expected


@pytest.mark.parametrize('timeintervalset, expected', [
    (TimeIntervalSet(
        [AND, TimeInterval(Interval(1, 15), Unit.YEAR, None)]
     ),
     [AND, [[1, 15], 'year', None]]),
    (TimeIntervalSet(
        [AND, TimeInterval(Interval(1, 25), Unit.DAY, Unit.WEEK)]
     ),
     [AND, [[1, 25], 'day', 'week']]),

])
def test_to_json(timeintervalset, expected):
    """Cases for `to_json()` method."""
    actual = timeintervalset.to_json()

    assert actual == expected


@pytest.mark.parametrize('value, expected', [
    (json.dumps([AND, [[0, 15], 'day', 'week']]),
     TimeIntervalSet(
         [AND, TimeInterval(Interval(0, 15), Unit.DAY, Unit.WEEK)]
     )),
    (json.dumps([AND, [[5, 25], 'year', None]]),
     TimeIntervalSet([AND, TimeInterval(Interval(5, 25), Unit.YEAR, None)])),
    ([AND, [[5, 25], 'year', None]],
     TimeIntervalSet([AND, TimeInterval(Interval(5, 25), Unit.YEAR, None)])),
    ([AND, [[5, 25], 'year', None], [NOT, [[10, 15], 'year', None]]],
     TimeIntervalSet(
         [AND, TimeInterval(Interval(5, 25), Unit.YEAR, None),
          [NOT, TimeInterval(Interval(10, 15), 'year', None)]]
     ))
])
def test_from_json(value, expected):
    """Cases for `from_json()` method."""
    actual = TimeIntervalSet.from_json(value)

    assert actual == expected
