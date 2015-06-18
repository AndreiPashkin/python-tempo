#!/usr/bin/env python
# coding=utf-8
import heapq
import datetime as dt
from tempo.schedule import Schedule

from tempo.utils import default


class ScheduleSet(object):
    def __init__(self, include, exclude=None):
        self.include = include = set(include)
        self.exclude = exclude = default(exclude, set())

    def __contains__(self, item):
        for exclude in self.exclude:
            if item in exclude:
                return False

        for include in self.include:
            if item in include:
                return True

        return False

    def forward(self, datetime=None):
        datetime = default(datetime, dt.datetime.now())

        include = {s.forward(datetime) for s in self.include}
        cache = []

        prev = None

        while True:
            for e in list(include):
                try:
                    d = next(e)
                    assert any(d in s for s in self.include)
                except StopIteration:
                    include.discard(e)
                    continue

                for exclude in self.exclude:
                    if d in exclude:
                        break
                else:
                    heapq.heappush(cache, d)

            try:
                next_ = heapq.heappop(cache)
                if prev is not None and not (next_ > prev):
                    continue
                yield next_
                prev = next_
            except IndexError:
                raise StopIteration
