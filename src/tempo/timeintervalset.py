# coding=utf-8
from collections import deque


NOT = 'NOT'
AND = 'AND'
OR  = 'OR'


_OPS = {NOT, AND, OR}


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
    result_stack.append(callback(*frame))


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
                if len(result_stack) == 1 and result_stack[0] not in _OPS:
                    break
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

    return result_stack.pop()


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
