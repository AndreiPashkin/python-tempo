# coding=utf-8


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

    def isoverlap(self, other):
        """Is this interval overlaps with other one?"""
        if other is EmptyInterval:
            return False
        return not (self.stop < other.start or self.start > other.stop)

    def overlap(self, other):
        """Returns a new instance of Interval, that represents overlap
        between this interval and a given one.

        If intervals does not overlap, `EmptyInterval` is returned.
        """
        if not self.isoverlap(other):
            return EmptyInterval
        elif self <= other:
            return self.__class__(other.start, other.stop)
        elif self > other:
            return self.__class__(self.start, self.stop)
        else:
            _, start, stop, _ = sorted((self.start, self.stop,
                                        other.start, other.stop))
            return self.__class__(start, stop)

    def combine(self, other):
        """If two intervals intersect, returns a new interval,
        that cover space of both. Otherwise - returns `EmptyInterval`.
        """
        if not self.isoverlap(other):
            return EmptyInterval

        start, _, _, stop = sorted((self.start, self.stop,
                                    other.start, other.stop))

        return self.__class__(start, stop)


class EmptyIntervalType(Interval):

    __slots__ = ()

    def __new__(cls, *args, **kwargs):
        global EmptyInterval

        if EmptyInterval is None:
            return super(EmptyIntervalType, cls).__new__(cls, *args, **kwargs)
        else:
            raise TypeError('Can not create new instances.')

    def __init__(self):
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

    def isoverlap(self, other):
        return False

    def overlap(self, other):
        return self

    def combine(self, other):
        return other


EmptyInterval = None
EmptyInterval = EmptyIntervalType()
