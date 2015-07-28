#!/usr/bin/env python
# coding=utf-8
from decimal import Decimal

from six import iteritems
from funclib.utils import resolve_args


class Interval(object):
    """
    Interval(stop)
    Interval(start, stop)

    Represents an interval between two numbers.

    Parameters
    ----------
    start : decimal.Decimal or float or int
        Start of the interval.
    stop : decimal.Decimal or float or int
        Inclusive stop of the interval.

    Examples
    --------
    >>> interval = Interval(5)
    >>> interval
    ... Interval(start=0.0, stop=5.0)
    >>> list(interval)
    ... [Decimal('0'), Decimal('1'), Decimal('2'), Decimal('3'), Decimal('4'),
    ...  Decimal('5')]
    >>> 3 in interval
    ... True
    >>> 10 in interval
    ... False
    """
    _DEFAULTS = {'start': 0}

    def __init__(self, *args, **kwargs):
        try:
            arguments = resolve_args(['stop'], args, kwargs)
        except TypeError:
            arguments = resolve_args(['start', 'stop'], args, kwargs,
                                     self._DEFAULTS)

        final_arguments = self._DEFAULTS.copy()
        final_arguments.update(arguments._asdict())
        final_arguments = {k: Decimal(str(v))
                           for k, v in iteritems(final_arguments)}

        self.__dict__.update(final_arguments)

    def __iter__(self):
        """Iteration over intervals values as 'decimal.Decimal'
        instances.
        """
        current = self.start

        while current <= self.stop:
            yield current
            current += 1

    def __contains__(self, item):
        """Containment test.

        Parameters
        ----------
        item : int or float or decimal.Decimal
            Number to test.

        Returns
        -------
        bool
        """
        return (item >= self.start and
                item <= self.stop)

    def __str__(self):
        return ('Interval(start={start}, stop={stop})'
                .format(start=repr(float(self.start)),
                        stop=repr(float(self.stop))))

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return (self.start == other.start and
                self.stop == other.stop)

    def __hash__(self):
        return hash((self.start, self.stop))
