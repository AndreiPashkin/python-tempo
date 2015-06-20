#!/usr/bin/env python
# coding=utf-8
import random as rnd

from tempo.schedule import Schedule


def schedule_kwargs():
    kwargs = {
        'years': sorted(
            rnd.sample(Schedule.YEARS,
                       rnd.randrange(1, len(Schedule.YEARS)))[:20]
        ),
        'months': sorted(
            rnd.sample(Schedule.MONTHS,
                       rnd.randrange(1, len(Schedule.MONTHS)))
        ),
        'days': sorted(rnd.sample(Schedule.DAYS,
                                  rnd.randrange(1, len(Schedule.DAYS)))),
        'weekdays': sorted(rnd.sample(Schedule.WEEKDAYS,
                           rnd.randrange(1, len(Schedule.WEEKDAYS)))),
        'hours': sorted(rnd.sample(Schedule.HOURS,
                        rnd.randrange(1, len(Schedule.HOURS)))),
        'minutes': sorted(rnd.sample(Schedule.MINUTES,
                          rnd.randrange(1, len(Schedule.MINUTES)))),
        'seconds': sorted(rnd.sample(Schedule.SECONDS,
                              rnd.randrange(1, len(Schedule.SECONDS)))),
        'seconds_of_the_day': sorted(
            rnd.sample(Schedule.SECONDS_OF_THE_DAY,
            rnd.randrange(1, len(Schedule.SECONDS_OF_THE_DAY)))
        )
    }

    composite = {
        'hours': sorted(rnd.sample(Schedule.HOURS,
                                   rnd.randrange(1, len(Schedule.HOURS)))),
        'minutes': sorted(rnd.sample(Schedule.MINUTES,
                                     rnd.randrange(1, len(Schedule.MINUTES)))),
        'seconds': sorted(rnd.sample(Schedule.SECONDS,
                                     rnd.randrange(1, len(Schedule.SECONDS)))),
    }
    seconds = {
        'seconds_of_the_day': sorted(
            rnd.sample(Schedule.SECONDS_OF_THE_DAY,
                       rnd.randrange(1, len(Schedule.SECONDS_OF_THE_DAY)))
        )
    }

    choice = rnd.randrange(3)
    if choice == 0:
        kwargs.update(composite)
        kwargs.update({'seconds_of_the_day': []})
    elif choice == 2:
        kwargs.update({
            'hours': [],
            'minutes': [],
            'seconds': [],
        })
        kwargs.update(seconds)
    elif choice == 3:
        kwargs.update(composite)
        kwargs.update(seconds)

    return kwargs
