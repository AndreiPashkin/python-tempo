# coding=utf-8
"""Provides SparseInterval class."""
import operator as op
from collections import deque

from six.moves import range  # pylint: disable=redefined-builtin


class SparseInterval(object):
    """Non-contigous interval."""
    __slots__ = ['_intervals']

    def __init__(self, *intervals):
        intervals = sorted((tuple(sorted(e)) for e in intervals),
                           key=op.itemgetter(0))

        self._union(intervals)
        self._intervals = intervals

    @staticmethod
    def _union(intervals):
        """Unions sub-intervals of 'intervals' in-place.
        Assumes that 'intervals' sorted by first component of sub-element."""
        while len(intervals) > 0:
            prev = intervals.pop(0)
            if prev[0] == prev[1]:
                continue
            break
        else:
            return intervals

        for _ in range(len(intervals)):
            cur = intervals.pop(0)
            if cur[0] == cur[1]:
                continue
            if prev[1] < cur[0]:
                intervals.append(prev)
                prev = cur
            else:
                prev = (prev[0], max(prev[1], cur[1]))

        intervals.append(prev)

        return intervals

    @staticmethod
    def _intersection(intervals):
        """Finds intersections of sub-intervals of 'intervals' in-place.
        Assumes that 'intervals' sorted by first component of sub-element."""
        prev = intervals.pop(0)
        for _ in range(0, len(intervals)):
            cur = intervals.pop(0)
            if prev[1] >= cur[0]:
                intervals.append((max(prev[0], cur[0]), min(prev[1], cur[1])))
            prev = cur

        return intervals

    def union(self, other):
        """Produces interval, that contains space from both."""
        intervals = deque()
        intervals.extend(self._intervals)
        intervals.extend(other._intervals)  # pylint: disable=protected-access
        intervals = sorted(intervals, key=op.itemgetter(0))

        self._union(intervals)

        return self.__class__(*intervals)

    def intersection(self, other):
        """Produces interval, that contains space,
        contained by this and in 'other' in the same time."""
        intervals = deque()
        intervals.extend(self._intervals)
        intervals.extend(other._intervals)  # pylint: disable=protected-access
        intervals = sorted(intervals, key=op.itemgetter(0))

        self._intersection(intervals)

        return self.__class__(*intervals)

    def difference(self, other):
        """Produces inerval, that contain space of this one, but doesn't
        contain space of the 'other'."""
        intervals = deque()
        for a, b in self._intervals:
            intersects = False
            for c, d in other._intervals:  # pylint: disable=protected-access
                if a < c < b:
                    intervals.append((a, c))
                    if not intersects:
                        intersects = True
                if a < d < b:
                    intervals.append((d, b))
                    if not intersects:
                        intersects = True
            if not intersects:
                intervals.append((a, b))

        return self.__class__(*intervals)

    def __eq__(self, other):
        return (self._intervals ==
                other._intervals)  # pylint: disable=protected-access

    def __hash__(self):
        return hash(self._intervals)

    def __repr__(self):
        return 'SparseInterval(*%s)' % self._intervals
