# coding=utf-8
import pytest

from tempo.interval import Interval
from tempo.timeinterval import TimeInterval

from tempo.timeintervalset import (AND, NOT, OR, _walk, TimeIntervalSet, Omit,
                                   EmptyResult)


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
    ((AND, [True, True]), callback, True),
    ((AND, [True, False]), callback, False),
    ((OR, [True, False]), callback, True),
    ((OR, [False, False]), callback, False),
    ((NOT, [False]), callback, True),
    ((NOT, [True]), callback, False),
    ((AND, [(OR, [False, (NOT, [False]), True, (NOT, [False])])]),
     callback, True),
    ((AND, [(OR, [False, (NOT, [False]), True, (NOT, [True])])]),
     callback, True),
    ((AND, [(NOT, [True]), True, (AND, [False, (NOT, [False])])]),
     callback, False),
    ((AND, [(NOT, [False]), True, (AND, [True, (NOT, [False])])]),
     callback, True),
])
def test_walk(expression, callback, expected):
    """Cases for expression evaluator - '_walk' function."""
    assert _walk(expression, callback) == expected


def test_walk_raises_empty_result():
    """If result of evaluation is empty, EmptyResult is raised."""
    expression = (OR, [True, False])

    def callback(*_):
        raise Omit

    with pytest.raises(EmptyResult):
        _walk(expression, callback)


@pytest.mark.parametrize('first, second, expected', [
    (TimeIntervalSet((AND, [
        TimeInterval(Interval(0, 5), 'hour', 'day'),
        (NOT, [TimeInterval(Interval(2, 3), 'hour', 'day')])
     ])),
     TimeIntervalSet((AND, [
        TimeInterval(Interval(0, 5), 'hour', 'day'),
        (NOT, [TimeInterval(Interval(2, 3), 'hour', 'day')])
     ])),
     True),
    (TimeIntervalSet((AND, [
        TimeInterval(Interval(0, 5), 'hour', 'day'),
        (NOT, [TimeInterval(Interval(2, 3), 'hour', 'day')])
     ])),
     TimeIntervalSet((AND, [
        TimeInterval(Interval(0, 5), 'hour', 'day'),
        (NOT, [TimeInterval(Interval(2, 4), 'hour', 'day')])
     ])),
     False),
])
def test_eq_hash(first, second, expected):
    """Cases for equality test and hashing."""
    assert (first == second) == expected

    if expected:
        assert hash(first) == hash(second)
