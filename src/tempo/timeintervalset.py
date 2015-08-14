# coding=utf-8
"""Provides TimeIntervalSet class."""
from collections import deque
import json

from six import string_types

from tempo.timeinterval import TimeInterval


NOT = 'NOT'
AND = 'AND'
OR  = 'OR'


_OPS = {NOT, AND, OR}


class Void(Exception):
    pass


class Result(object):
    """Callback result wrapper.

    Intended to be used to avoid confusion between expressions
    and callback results, in case if they are expressions themselves.
    """
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return 'Result({})'.format(repr(self.value))


def _evaluate(result_stack, callback):
    """Evaluates topmost operator in 'result_stack' and appends
    the result of evaluation back.

    Parameters
    ----------
    result_stack : deque
        A stack with operators and arguments for them.
    callback : Callable
        A callback with the same signature as for `_walk()` function.
    """
    frame = deque()
    while True:
        item = result_stack.pop()
        frame.appendleft(item)
        if isinstance(item, string_types) and item in _OPS:
            if item == NOT:
                assert len(frame) == 2
            break
    try:
        result_stack.append(callback(*frame))
    except Void:
        pass


def _isexpression(value):
    """Checks if 'value' is an expression."""
    return (isinstance(value, (tuple, list, deque)) and
            len(value) > 0 and
            isinstance(value[0], string_types) and
            value[0] in _OPS)


def _walk(expression, callback):
    """Walks the 'expression' and applies 'callback' to operators and
    their arguments.

    Parameters
    ----------
    expression : tuple
        A nested structure of such form::

        <node>        ::= object|<expression>
        <operator>    ::= AND|OR|NOT
        <expression> ::= (<operator>, <node>, ...)

        It consists of tuples where the first element is an
        operator and an the other elements are an arguments
        for the operator. It can contain sub-expressions or objects,
        which are considered "atomic" and are passed to a 'callback'
        as is.

        Operators AND and OR accept arbitrary number of arguments, and
        NOT accept only one.

    callback : callable
        An expression evaluator callable, that accepts an operator as a
        first positional argument and an arguments for the operator
        as a variadic positional arguments.
        ::

            callback(operator, *args)

        `args` may be an "atomic" objects, that were included in the
        expression, or anything that the callback returned as a result
        of evaluation of previous expressions.
        A callback can raise Void exception to omit storing a returned
        value.

    Returns
    -------
    object
        A final result of the 'expression' evaluation, returned
        by the 'callback'.
    """
    stack = deque([deque([expression])])
    result_stack = deque()

    while len(stack) > 0:
        current = stack[-1]

        while True:
            if not (len(current) > 0):  # pylint: disable=superfluous-parens
                del stack[-1]
                if _isexpression(result_stack):
                    _evaluate(result_stack, callback)
                break

            item = current.popleft()
            if _isexpression(item):
                operator, values = item[0], item[1:]
                result_stack.append(operator)
                stack.append(deque(values))
                break
            else:
                result_stack.append(item)
    try:
        return result_stack.pop()
    except IndexError:
        raise Void


class TimeIntervalSet(object):
    """A set of time intervals, combined with a set logic operators:
    AND, OR and NOT.

    Parameters
    ----------
    expression : tuple
        A nested expression, composed of operators and arguments, which
        are `TimeInterval` instances or sub-expressions.
        Example of an expression::

            (AND,
                TimeInterval(Interval(10, 19), 'hour', 'day'),
                (NOT, TimeInterval(Interval(14, 15), 'hour', 'day')),
                (NOT, TimeInterval(Interval(6, 7), 'day', 'week')),
            ])

        It means: 'From 10:00 to 19:00 every day, except from
        14:00 to 15:00, and weekends'.
    """
    def __init__(self, expression):
        self.expression = expression

    def __str__(self):
        return 'TimeIntervalSet({})'.format(repr(self.expression))

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def _unnest(sample, operator, *args):
        """Collects operators and arguments to a flat
        'sample' collection."""
        sample.append(operator)
        sample.extend(args)
        raise Void

    def __eq__(self, other):
        sample_self = []
        sample_other = []

        try:
            _walk(self.expression,
                  lambda op, *args: self._unnest(sample_self, op, *args))
        except Void:
            pass

        try:
            _walk(other.expression,
                  lambda op, *args: self._unnest(sample_other, op, *args))
        except Void:
            pass

        return tuple(sample_self) == tuple(sample_other)

    def __hash__(self):
        sample = []

        try:
            _walk(self.expression,
                  lambda op, *args: self._unnest(sample, op, *args))
        except Void:
            pass

        return hash(tuple(sample))

    def __contains__(self, item):
        """Containment test. Accepts whatever TimeInterval can
        test for containment.
        """
        def callback(operator, *args):
            """Performs a containment test or all arguments
            of an operator and then applies operator rules to a
            results.
            """
            contains = []
            for arg in args:
                if isinstance(arg, bool):
                    contains.append(arg)
                else:
                    contains.append(item in arg)

            if operator == AND:
                return all(contains)
            elif operator == OR:
                return any(contains)
            elif operator == NOT:
                return not contains[0]

        return _walk(self.expression, callback)

    @staticmethod
    def to_json_callback(operator, *args):
        """Converts arguments that are time intervals to JSON."""
        result = [operator]
        for arg in args:
            if isinstance(arg, TimeInterval):
                arg = arg.to_json()
            result.append(arg)
        return result

    def to_json(self):
        """Exports `TimeIntervalSet` instance to JSON serializable
        representation."""
        return _walk(self.expression, self.to_json_callback)

    @staticmethod
    def from_json_callback(operator, *args):
        """Converts arguments that are time intervals to Python."""
        result = [operator]
        for arg in args:
            if isinstance(arg, (list, tuple)):
                arg = TimeInterval.from_json(arg)
            elif isinstance(arg, Result):
                arg = arg.value
            result.append(arg)
        return Result(result)

    @classmethod
    def from_json(cls, value):
        """Constructs `TimeIntervalSet` instance from JSON serializable
        representation or from JSON string."""
        if not isinstance(value, (tuple, list)):
            value = json.loads(value)
        return cls(_walk(value, cls.from_json_callback).value)
