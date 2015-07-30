# coding=utf-8
import random as rnd

from tempo.unit import Unit, UNIT_ORDER

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
       (recurrence is None or UNIT_ORDER[unit] < UNIT_ORDER[recurrence])
]
