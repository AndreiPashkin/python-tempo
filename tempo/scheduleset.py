#!/usr/bin/env python
# coding=utf-8
import heapq
import datetime as dt

from tempo.utils import default


class ScheduleSet(object):
    def __init__(self, include, exclude=None):
        self.include = set(include)
        self.exclude = default(exclude, {})
        maxs = [s.max for s in include
                if all(s.max not in e for e in exclude)]
        if maxs:
            self.max = max(maxs)
        else:
            self.max = None
        mins = [s.min for s in include
                if all(s.min not in e for e in exclude)]
        if mins:
            self.min = min(mins)
        else:
            self.min = None

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
