#!/usr/bin/env python
# coding=utf-8
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
    >>> 3 in interval
    ... True
    >>> 10 in interval
    ... False
    """
    _DEFAULTS = {'start': 0}

    __slots__ = ('start', 'stop')

    def __init__(self, *args, **kwargs):
        try:
            arguments = resolve_args(['stop'], args, kwargs)
        except TypeError:
            arguments = resolve_args(['start', 'stop'], args, kwargs,
                                     self._DEFAULTS)

        final = self._DEFAULTS.copy()
        final.update(arguments._asdict())

        self.start, self.stop = final['start'], final['stop']
        assert self.start <= self.stop

    def __str__(self):
        return ('Interval(start={start}, stop={stop})'
                .format(start=repr(float(self.start)),
                        stop=repr(float(self.stop))))

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash((self.start, self.stop))

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
        return self.start <= item <= self.stop

    def __eq__(self, other):
        return (self.start == other.start and
                self.stop == other.stop)

    def __gt__(self, other):
        return self.start < other.start and self.stop > other.stop

    def __ge__(self, other):
        return self.start <= other.start and self.stop >= other.stop

    def __lt__(self, other):
        return self.start > other.start and self.stop < other.stop

    def __le__(self, other):
        return self.start >= other.start and self.stop <= other.stop
