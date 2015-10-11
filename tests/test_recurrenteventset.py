
# coding=utf-8
import datetime as dt
import json
from functools import partial
import itertools as it

import pytest

from tempo.recurrentevent import RecurrentEvent

from tempo.recurrenteventset import (AND, NOT, OR, _walk, RecurrentEventSet, Void)
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
    (RecurrentEventSet((AND,
        RecurrentEvent(0, 5, 'hour', 'day'),
        (NOT, RecurrentEvent(2, 3, 'hour', 'day'))
     )),
     RecurrentEventSet((AND,
        RecurrentEvent(0, 5, 'hour', 'day'),
        (NOT, RecurrentEvent(2, 3, 'hour', 'day'))
     )),
     True),
    (RecurrentEventSet((AND,
        RecurrentEvent(0, 5, 'hour', 'day'),
        (NOT, RecurrentEvent(2, 3, 'hour', 'day'))
     )),
     RecurrentEventSet((AND,
        RecurrentEvent(0, 5, 'hour', 'day'),
        (NOT, RecurrentEvent(2, 4, 'hour', 'day'))
     )),
     False),
])
def test_eq_hash(first, second, expected):
    """Cases for equality test and hashing."""
    assert (first == second) == expected

    if expected:
        assert hash(first) == hash(second)


def test_eq_with_other_type():
    """Equality for object with othery type should not throw exceptions
    and return False."""
    recurrenteventset = RecurrentEventSet.from_json([AND, 0, 10, 'hour', 'day'])
    other = object()

    assert not (recurrenteventset == other)


def pg_contains(item, expression, connection):
    """PostgreSQL binding RecurrentEventSet containment test
    implementation."""
    if isinstance(item, tuple):
        item = list(item)

    recurrenteventset = RecurrentEventSet(expression).to_json()
    with connection.cursor() as cursor:
        cursor.execute(
            '''SELECT tempo_recurrenteventset_contains(%s, %s)''',
            (json.dumps(recurrenteventset), item)
        )
        return cursor.fetchone()[0]


def py_contains(item, expression):
    """Python RecurrentEventSet containment test
    implementation."""
    return item in RecurrentEventSet(expression)


@pytest.fixture(params=Implementation.values())
def recurrenteventset_contains(request):
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
     (AND, RecurrentEvent(2, 8, 'month', 'year')),
     True),
    (dt.datetime(2005, 12, 15),
     (AND, RecurrentEvent(2, 8, 'month', 'year')),
     False),
    (dt.datetime(2005, 5, 15),
     (AND, RecurrentEvent(2, 8, 'month', 'year'),
            (NOT, RecurrentEvent(4, 5, 'month', 'year'))),
     True),
])
def test_contains(item, expression, expected, recurrenteventset_contains):
    """Cases for containment test."""
    assert recurrenteventset_contains(item, expression) == expected


@pytest.mark.parametrize('recurrenteventset, expected', [
    (RecurrentEventSet(
        [AND, RecurrentEvent(1, 15, Unit.YEAR, None)]
     ),
     [AND, [1, 15, 'year', None]]),
    (RecurrentEventSet(
        [AND, RecurrentEvent(1, 25, Unit.DAY, Unit.WEEK)]
     ),
     [AND, [1, 25, 'day', 'week']]),
    (RecurrentEventSet(
         [AND, RecurrentEvent(5, 25, Unit.YEAR, None),
          [NOT, RecurrentEvent(10, 15, 'year', None)]]
     ),
     [AND, [5, 25, 'year', None], [NOT, [10, 15, 'year', None]]]),
])
def test_to_json(recurrenteventset, expected):
    """Cases for `to_json()` method."""
    actual = recurrenteventset.to_json()

    assert actual == expected


@pytest.mark.parametrize('value, expected', [
    (json.dumps([AND, [0, 15, 'day', 'week']]),
     RecurrentEventSet(
         [AND, RecurrentEvent(0, 15, Unit.DAY, Unit.WEEK)]
     )),
    (json.dumps([AND, [5, 25, 'year', None]]),
     RecurrentEventSet([AND, RecurrentEvent(5, 25, Unit.YEAR, None)])),
    ([AND, [5, 25, 'year', None]],
     RecurrentEventSet([AND, RecurrentEvent(5, 25, Unit.YEAR, None)])),
    ([AND, [5, 25, 'year', None], [NOT, [10, 15, 'year', None]]],
     RecurrentEventSet(
         [AND, RecurrentEvent(5, 25, Unit.YEAR, None),
          [NOT, RecurrentEvent(10, 15, 'year', None)]]
     ))
])
def test_from_json(value, expected):
    """Cases for `from_json()` method."""
    actual = RecurrentEventSet.from_json(value)

    assert actual == expected


def py_forward(expression, start, trim, n):
    """Python API for RecurrentEventSet.forward()"""
    return list(it.islice(RecurrentEventSet.from_json(expression)
                                         .forward(start, trim), n))


def pg_forward(expression, start, trim, n, connection):
    """PostgreSQL API for RecurrentEventSet.forward()."""

    recurrenteventset = RecurrentEventSet.from_json(expression).to_json()
    with connection.cursor() as cursor:
        cursor.execute(
            '''SELECT * FROM tempo_recurrenteventset_forward(%s, %s, %s, %s)''',
            (json.dumps(recurrenteventset), start, n, trim)
        )

        return list(cursor.fetchall())


@pytest.fixture(params=Implementation.values())
def recurrenteventset_forward(request):
    """Various APIs for RecurrentEventSet.forwars()."""
    if request.param == Implementation.PYTHON:
        return py_forward
    elif request.param == Implementation.POSTGRESQL:
        connection = request.getfuncargvalue('connection')
        request.getfuncargvalue('postgresql_tempo')
        request.getfuncargvalue('transaction')
        return partial(pg_forward, connection=connection)
    else:
        raise NotImplemented


@pytest.mark.parametrize('expression, start, trim, expected', [
    ([OR, [1, 15, 'day', 'month'], [15, 20, 'day', 'month']],
     dt.datetime(2000, 1, 1), True,
     [(dt.datetime(2000, 1, 1), dt.datetime(2000, 1, 20)),
      (dt.datetime(2000, 2, 1), dt.datetime(2000, 2, 20))]),
    ([AND, [1, 15, 'day', 'month'], [10, 20, 'day', 'month']],
     dt.datetime(2000, 1, 1), True,
     [(dt.datetime(2000, 1, 10), dt.datetime(2000, 1, 15)),
      (dt.datetime(2000, 2, 10), dt.datetime(2000, 2, 15))]),
    ([AND, [1, 25, 'day', 'month'], [NOT, [10, 15, 'day', 'month']]],
     dt.datetime(2000, 1, 1), True,
     [(dt.datetime(2000, 1, 1), dt.datetime(2000, 1, 10)),
      (dt.datetime(2000, 1, 15), dt.datetime(2000, 1, 25))]),
    ([AND, [1, 10, 'day', 'month'], [15, 20, 'day', 'month']],
     dt.datetime(2000, 1, 1), True,
     []),
    ([AND, [5, 10, 'day', 'month'], [15, 20, 'hour', 'day']],
     dt.datetime(2000, 1, 1), True,
     [(dt.datetime(2000, 1, 5, 15), dt.datetime(2000, 1, 5, 20)),
      (dt.datetime(2000, 1, 6, 15), dt.datetime(2000, 1, 6, 20))]),
    ([OR, [5, 10, 'day', 'month']],
     dt.datetime(2000, 1, 8), False,
     [(dt.datetime(2000, 1, 5), dt.datetime(2000, 1, 10)),
      (dt.datetime(2000, 2, 5), dt.datetime(2000, 2, 10)),]),
    ((OR,
        (AND, [1, 4, 'day', 'week'], [10, 19, 'hour', 'day']),
        (AND, [5, 6, 'day', 'week'], [10, 16, 'hour', 'day'])),
     dt.datetime(2000, 1, 1), False,
     [(dt.datetime(2000, 1, 3, 10, 0), dt.datetime(2000, 1, 3, 19, 0)),
      (dt.datetime(2000, 1, 4, 10, 0), dt.datetime(2000, 1, 4, 19, 0)),
      (dt.datetime(2000, 1, 5, 10, 0), dt.datetime(2000, 1, 5, 19, 0))])
])
def test_forward(expression, start, trim, expected, recurrenteventset_forward):
    """Various forward() cases."""
    actual = recurrenteventset_forward(expression, start, trim, len(expected))

    print(actual)
    print(expected)
    assert actual == expected


@pytest.mark.parametrize('expression, expected', [
    ([AND, [1, 5, "month", "year"], [NOT, [1, 15, "day", "month"]]], True),
    ([AND, [1, 2, "months", "year"]], False),
    ('["AND", [1, 2, "month", "year"]]', True),
])
def test_validate_json(expression, expected):
    """Cases for RecurrentEventSet.validate_json()."""
    assert RecurrentEventSet.validate_json(expression) == expected
