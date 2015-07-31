# coding=utf-8
import datetime as dt
import random as rnd

from tempo.timeutils import floor, delta, add_delta
from tempo.unit import Unit, ORDER, MIN, MAX, BASE

from itertools import permutations


def randuniq(n, *args, **kwargs):
    """The same as `random.randrange()`, but generates a sequence
    of unique pseudo-random numbers of size 'n'.

    Notes
    -----
    Quick and dirty implementation with try/test approach.
    """
    result = set()
    tries = 0
    while True:
        tries += 1
        size = len(result)
        result.add(rnd.randrange(*args, **kwargs))
        if len(result) > size:
            tries = 0
        elif tries > 1000:
            raise RuntimeError

        if len(result) >= n:
            return list(result)


# All possible valid combinations of unit and recurrence.
CASES = [
    (unit, recurrence)
    for unit, recurrence in
    permutations([None, Unit.YEAR, Unit.MONTH, Unit.WEEK,
                  Unit.DAY, Unit.HOUR, Unit.MINUTE, Unit.SECOND], 2)
    if unit is not None and
       (recurrence is None or ORDER[unit] < ORDER[recurrence])
]


def random_datetime_between(datetime1, datetime2):
    """Random `datetime.datetime` object lying between
    'datetime1' and 'datetime2'."""
    assert datetime2 > datetime1

    delta = datetime2 - datetime1
    return datetime1 + dt.timedelta(
        seconds=rnd.randrange(delta.total_seconds())
    )


def sample(unit):
    """Random time between between bounds of possible time.

    Returned time is not included in the last segment of
    interval measured in 'unit'.
    """
    return floor(random_datetime_between(MIN, add_delta(MAX, -1, unit)), unit)


def guess(lower, upper, n, test):
    """Guesses 'n' random integers within 'lower' and 'upper' boundaries,
    that satisfy 'test'."""
    for _ in range(1000 * n):
        results = tuple(rnd.randint(lower, upper) for _ in range(n))
        if test(*results):
            return results
    else:
        raise RuntimeError


def unit_span(unit, recurrence=None, sample=None):
    """How much 'unit''s in 'recurrence'."""
    lower = BASE[unit]

    assert ((recurrence is None and sample is None) or
            (recurrence is not None and sample is not None))

    if recurrence is not None:
        upper = delta(sample, add_delta(sample, 1, recurrence),
                                        unit)
    else:
        upper = delta(MIN, add_delta(MAX, -1, unit), unit)

    assert lower != upper and lower < upper

    return lower, upper
