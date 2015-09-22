# coding=utf-8
import datetime as dt
import json
from functools import partial
import itertools as it

import pytest

from tempo.timeinterval import TimeInterval

from tempo.timeintervalset import (AND, NOT, OR, _walk, TimeIntervalSet, Void)
from tempo.unit import Unit
from tests import Implementation


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
        TimeInterval(0, 5, 'hour', 'day'),
        (NOT, TimeInterval(2, 3, 'hour', 'day'))
     )),
     TimeIntervalSet((AND,
        TimeInterval(0, 5, 'hour', 'day'),
        (NOT, TimeInterval(2, 3, 'hour', 'day'))
     )),
     True),
    (TimeIntervalSet((AND,
        TimeInterval(0, 5, 'hour', 'day'),
        (NOT, TimeInterval(2, 3, 'hour', 'day'))
     )),
     TimeIntervalSet((AND,
        TimeInterval(0, 5, 'hour', 'day'),
        (NOT, TimeInterval(2, 4, 'hour', 'day'))
     )),
     False),
])
def test_eq_hash(first, second, expected):
    """Cases for equality test and hashing."""
    assert (first == second) == expected

    if expected:
        assert hash(first) == hash(second)


def pg_contains(item, expression, connection):
    """PostgreSQL binding TimeIntervalSet containment test
    implementation."""
    if isinstance(item, tuple):
        item = list(item)

    timeintervalset = TimeIntervalSet(expression).to_json()
    with connection.cursor() as cursor:
        cursor.execute(
            '''SELECT tempo_timeintervalset_contains(%s, %s)''',
            (json.dumps(timeintervalset), item)
        )
        return cursor.fetchone()[0]


def py_contains(item, expression):
    """Python TimeIntervalSet containment test
    implementation."""
    return item in TimeIntervalSet(expression)


@pytest.fixture(params=Implementation.values())
def timeintervalset_contains(request):
    if request.param == Implementation.PYTHON:
        return py_contains
    elif request.param == Implementation.POSTGRESQL:
        connection = request.getfuncargvalue('connection')
        request.getfuncargvalue('postgresql_tempo')
        request.getfuncargvalue('transaction')
        return partial(pg_contains, connection=connection)
    else:
        raise NotImplemented


@pytest.mark.parametrize('item, expression, expected', [
    (dt.datetime(2005, 5, 15),
     (AND, TimeInterval(2, 8, 'month', 'year')),
     True),
    (dt.datetime(2005, 12, 15),
     (AND, TimeInterval(2, 8, 'month', 'year')),
     False),
    (dt.datetime(2005, 5, 15),
     (AND, TimeInterval(2, 8, 'month', 'year'),
            (NOT, TimeInterval(4, 5, 'month', 'year'))),
     True),
])
def test_contains(item, expression, expected, timeintervalset_contains):
    """Cases for containment test."""
    assert timeintervalset_contains(item, expression) == expected


@pytest.mark.parametrize('timeintervalset, expected', [
    (TimeIntervalSet(
        [AND, TimeInterval(1, 15, Unit.YEAR, None)]
     ),
     [AND, [[1, 15], 'year', None]]),
    (TimeIntervalSet(
        [AND, TimeInterval(1, 25, Unit.DAY, Unit.WEEK)]
     ),
     [AND, [[1, 25], 'day', 'week']]),
    (TimeIntervalSet(
         [AND, TimeInterval(5, 25, Unit.YEAR, None),
          [NOT, TimeInterval(10, 15, 'year', None)]]
     ),
     [AND, [[5, 25], 'year', None], [NOT, [[10, 15], 'year', None]]]),
])
def test_to_json(timeintervalset, expected):
    """Cases for `to_json()` method."""
    actual = timeintervalset.to_json()

    assert actual == expected


@pytest.mark.parametrize('value, expected', [
    (json.dumps([AND, [[0, 15], 'day', 'week']]),
     TimeIntervalSet(
         [AND, TimeInterval(0, 15, Unit.DAY, Unit.WEEK)]
     )),
    (json.dumps([AND, [[5, 25], 'year', None]]),
     TimeIntervalSet([AND, TimeInterval(5, 25, Unit.YEAR, None)])),
    ([AND, [[5, 25], 'year', None]],
     TimeIntervalSet([AND, TimeInterval(5, 25, Unit.YEAR, None)])),
    ([AND, [[5, 25], 'year', None], [NOT, [[10, 15], 'year', None]]],
     TimeIntervalSet(
         [AND, TimeInterval(5, 25, Unit.YEAR, None),
          [NOT, TimeInterval(10, 15, 'year', None)]]
     ))
])
def test_from_json(value, expected):
    """Cases for `from_json()` method."""
    actual = TimeIntervalSet.from_json(value)

    assert actual == expected


def py_forward(expression, start, n):
    """Python API for TimeIntervalSet.forward()"""
    return list(it.islice(TimeIntervalSet.from_json(expression)
                                         .forward(start), n))


def pg_forward(expression, start, n, connection):
    """PostgreSQL API for TimeIntervalSet.forward()."""

    timeintervalset = TimeIntervalSet.from_json(expression).to_json()
    with connection.cursor() as cursor:
        cursor.execute(
            '''SELECT * FROM tempo_timeintervalset_forward(%s, %s, %s)''',
            (json.dumps(timeintervalset), start, n)
        )

        return list(cursor.fetchall())


@pytest.fixture(params=Implementation.values())
def timeintervalset_forward(request):
    """Various APIs for TimeIntervalSet.forwars()."""
    if request.param == Implementation.PYTHON:
        return py_forward
    elif request.param == Implementation.POSTGRESQL:
        connection = request.getfuncargvalue('connection')
        request.getfuncargvalue('postgresql_tempo')
        request.getfuncargvalue('transaction')
        return partial(pg_forward, connection=connection)
    else:
        raise NotImplemented


@pytest.mark.parametrize('expression, start, expected', [
    ([OR, [[1, 15], 'day', 'month'], [[15, 20], 'day', 'month']],
     dt.datetime(2000, 1, 1),
     [(dt.datetime(2000, 1, 1), dt.datetime(2000, 1, 20)),
      (dt.datetime(2000, 2, 1), dt.datetime(2000, 2, 20))]),
    ([AND, [[1, 15], 'day', 'month'], [[10, 20], 'day', 'month']],
     dt.datetime(2000, 1, 1),
     [(dt.datetime(2000, 1, 10), dt.datetime(2000, 1, 15)),
      (dt.datetime(2000, 2, 10), dt.datetime(2000, 2, 15))]),
    ([AND, [[1, 25], 'day', 'month'], [NOT, [[10, 15], 'day', 'month']]],
     dt.datetime(2000, 1, 1),
     [(dt.datetime(2000, 1, 1), dt.datetime(2000, 1, 10)),
      (dt.datetime(2000, 1, 15), dt.datetime(2000, 1, 25))]),
    ([AND, [[1, 10], 'day', 'month'], [[15, 20], 'day', 'month']],
     dt.datetime(2000, 1, 1),
     []),
    ([AND, [[5, 10], 'day', 'month'], [[15, 20], 'hour', 'day']],
     dt.datetime(2000, 1, 1),
     [(dt.datetime(2000, 1, 5, 15), dt.datetime(2000, 1, 5, 20)),
      (dt.datetime(2000, 2, 5, 15), dt.datetime(2000, 2, 5, 20))]),
])
def test_forward(expression, start, expected, timeintervalset_forward):
    """Various forward() cases."""
    actual = timeintervalset_forward(expression, start, len(expected))

    assert actual == expected
