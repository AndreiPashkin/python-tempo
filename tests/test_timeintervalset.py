# coding=utf-8
import pytest

from tempo.timeintervalset import AND, NOT, OR, _walk


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
