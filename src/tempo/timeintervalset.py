# coding=utf-8
"""Provides TimeIntervalSet class."""
import itertools as it
from collections import deque
import json

from six import string_types
from six.moves import reduce  # pylint: disable=redefined-builtin

from tempo.timeinterval import TimeInterval
from tempo.sparseinterval import SparseInterval
from tempo.unit import MIN, MAX


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

    def forward(self, start):
        """Generates intervals according to the expression.

        Intervals never overlap.
        Each next interval is largest possbile interval.

        Parameters
        ----------
        start : datetime.datetime
            Inclusive start date.

        Yields
        ------
        tuple
            Inclusive start and non-inclusive dates of an interval.

        Notes
        -----
        The alghorithm is simple:

            1. It generates intervals from TimeInterval instances and
               applies set logic operators on them.
            2. Checks if resulting interval has gap.
            3. Checks if there is a possibility, that this gap will gone,
               by checking if some of the generators could possibly generate
               interval that will intersect with gap.
            4. If checks succeed, yields interval previous to gap.
            5. If not - iterates generators until check succeed.

        This implementation if fairly ineffective and should be otimized.
        """
        context = {
            'all': []
        }

        def prepare(operator, *args):
            """Initializes forward() generators of TimeIntervals."""
            prepared = [operator]
            for arg in args:
                if isinstance(arg, TimeInterval):
                    arg = {
                        'generator': arg.forward(start),
                        'results': SparseInterval(),
                        'exhausted': False
                    }
                    context['all'].append(arg)
                elif isinstance(arg, Result):
                    arg = arg.value
                prepared.append(arg)

            return Result(prepared)

        generators = _walk(self.expression, prepare).value

        def generate(operator, *args):
            """Generates SparseInterval instance current and past
            results of TimeInterval.forward() generators with respect
            to 'operator' of given expression."""
            operands = []
            for arg in args:
                if isinstance(arg, dict):
                    try:
                        result = next(arg['generator'])
                        arg['results'] = (
                            arg['results'].union(SparseInterval(*[result]))
                        )
                    except StopIteration:
                        arg['exhausted'] = True
                    operands.append(arg['results'])
                elif isinstance(arg, SparseInterval):
                    operands.append(arg)
            if operator == AND:
                return reduce(lambda m, v: m.intersection(v), operands)
            elif operator == OR:
                return reduce(lambda m, v: m.union(v), operands)
            elif operator == NOT:
                union = reduce(lambda m, v: m.union(v), operands)
                intervals = it.chain((MIN,),
                                     it.chain.from_iterable(union.intervals),
                                     (MAX,))
                return SparseInterval(*zip(intervals, intervals))
            else:
                raise AssertionError

        last_date = None
        while True:
            generated = _walk(generators, generate)

            if (len(generated.intervals) == 0 and
                all(e['exhausted'] for e in context['all'])):
                return

            # Has gap
            if len(generated.intervals) > 1:
                if last_date is None:
                    last_date = generated.intervals[0][1]

                for item in context['all']:
                    if len(item['results'].intervals) == 0:
                        continue
                    if (item['results'].intervals[-1][1] < last_date and
                        not item['exhausted']):
                        break
                else:
                    yield next((a, b) for a, b in generated.intervals
                               if b == last_date)
                    last_date = next(b for _, b in generated.intervals
                                     if b > last_date)

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
