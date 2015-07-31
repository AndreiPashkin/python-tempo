# coding=utf-8
from collections import deque


NOT = 'NOT'
AND = 'AND'
OR  = 'OR'


_OPS = {NOT, AND, OR}


class Omit(Exception):
    pass


class EmptyResult(Exception):
    pass


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
        e = result_stack.pop()
        frame.appendleft(e)
        if e in _OPS:
            if e == NOT:
                assert len(frame) == 2
            break
    try:
        result_stack.append(callback(*frame))
    except Omit:
        pass


def _walk(expression, callback):
    """Walks the 'expression' and applies 'callback' to operators and
    their arguments.

    Parameters
    ----------
    expression : tuple
        A nested structure of such form::

        <node>        ::= object|<expression>
        <operator>    ::= AND|OR|NOT
        <expression> ::= (<operator>, [<node>, ...])

        It consists of pair-tuples where the first element is an
        operator and an the second element is a list of an arguments
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

            callback(op, *args)

        `args` may be an "atomic" objects, that were included in the
        expression, or anything that the callback returned as a result
        of evaluation of previous expressions.
        A callback can raise Omit exception to omit storing a returned
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
            if not (len(current) > 0):
                del stack[-1]
                if len(result_stack) > 0 and result_stack[0] in _OPS:
                    _evaluate(result_stack, callback)
                break

            e = current.popleft()
            if isinstance(e, tuple):
                op, values = e
                result_stack.append(op)
                stack.append(deque(values))
                break
            else:
                result_stack.append(e)
    try:
        return result_stack.pop()
    except IndexError:
        raise EmptyResult


class TimeIntervalSet(object):
    """A set of time intervals, combined with a set logic operators:
    AND, OR and NOT.

    Parameters
    ----------
    expression : tuple
        A nested expression, composed of operators and arguments, which
        are `TimeInterval` instances or sub-expressions.
        Example of an expression::

            (AND, [
                TimeInterval(Interval(10, 19), 'hour', 'day'),
                (NOT, [TimeInterval(Interval(14, 15), 'hour', 'day')]),
                (NOT, [TimeInterval(Interval(6, 7), 'day', 'week')]),
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

    def __eq__(self, other):
        sample_self = []
        sample_other = []

        def callback(sample, op, *args):
            sample.append(op)
            sample.extend(args)
            raise Omit

        try:
            _walk(self.expression,
                 lambda op, *args: callback(sample_self, op, *args))
        except EmptyResult:
            pass

        try:
            _walk(other.expression,
                 lambda op, *args: callback(sample_other, op, *args))
        except EmptyResult:
            pass

        return tuple(sample_self) == tuple(sample_other)

    def __hash__(self):
        sample = []

        def callback(op, *args):
            sample.append(op)
            sample.extend(args)
            raise Omit

        try:
            _walk(self.expression, callback)
        except EmptyResult:
            pass

        return hash(tuple(sample))

    def __contains__(self, item):
        """Containment test. Accepts whatever TimeInterval can
        test for containment.
        """
        def callback(op, *args):
            contains = []
            for arg in args:
                if isinstance(arg, bool):
                    contains.append(arg)
                else:
                    contains.append(item in arg)

            if op == AND:
                return all(contains)
            elif op == OR:
                return any(contains)
            elif op == NOT:
                return not contains[0]

        return _walk(self.expression, callback)
