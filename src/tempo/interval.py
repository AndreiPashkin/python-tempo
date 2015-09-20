# coding=utf-8
"""Provides Interval class and EmptyInterval singleton value."""


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

    __slots__ = ('start', 'stop')

    def __init__(self, *args, **kwargs):
        try:
            self.stop = kwargs.get('stop', args[1])
            self.start = kwargs.get('start', args[0])
        except IndexError:
            self.start = 0
            self.stop = kwargs.get('start', args[0])

    def __str__(self):
        return ('Interval(start={start}, stop={stop})'
                .format(start=repr(self.start),
                        stop=repr(self.stop)))

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


class EmptyIntervalType(Interval):
    """A class of EmptyInterval singleton value."""

    __slots__ = ()

    def __new__(cls, *args, **kwargs):
        global EmptyInterval  # pylint: disable=W0602,C0103

        if EmptyInterval is None:
            return super(EmptyIntervalType, cls).__new__(cls, *args, **kwargs)
        else:
            raise TypeError('Can not create new instances.')

    def __init__(self):  # pylint: disable=super-init-not-called
        pass

    def __str__(self):
        return 'EmptyInterval'

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return True
        else:
            return False

    def __hash__(self):
        return 185453665

    def __contains__(self, item):
        return False

    def __gt__(self, other):
        return False

    def __ge__(self, other):
        return self.__eq__(other)

    def __lt__(self, other):
        return not self.__eq__(other)

    def __le__(self, other):
        return True

# pylint: disable=invalid-name
EmptyInterval = None
EmptyInterval = EmptyIntervalType()
