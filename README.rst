=====
Tempo
=====

.. image:: https://travis-ci.org/AndrewPashkin/python-tempo.svg?branch=master
   :alt: Build Status
   :target: https://travis-ci.org/AndrewPashkin/python-tempo

.. image:: https://coveralls.io/repos/AndrewPashkin/python-tempo/badge.svg?branch=master&service=github
   :alt: Coverage
   :target: https://coveralls.io/github/AndrewPashkin/python-tempo?branch=master

This project is a scheduling library, written in Python, that provides a
generic way to compose and query schedules of continuous recurrent events,
such as working time of organizations, meetings, movie shows, etc.

It contains a Python implementation and bindings for PostgreSQL,
Django and Django REST Framework.

Links
=====
:PyPI: https://pypi.python.org/pypi/python-tempo
:Documentation: https://python-tempo.readthedocs.org/
:Issues: https://github.com/AndrewPashkin/python-tempo/issues/
:Code: https://github.com/AndrewPashkin/python-tempo/

Features
========
- Flexible schedule model, that can express schedules, that other libraries
  can't.
- Queries: containment of a single timestamp, future occurrences.
- Bindings:

  * PostgreSQL

    + Domain type for storing schedules
    + Procedures for performing tests on them
      (timestamp containment, future occurrences).

  * Django

    + Model field
    + Django-Admin widget
    + Custom lookups
      (timestamp containment,
      intersection with interval between two timestamps,
      test if scheduled event occurs within given interval
      between two timestamps).

  * Django-REST-Framework

    + Serializer field for serializing and deserializing schedules.

Quick example
=============
Just a short example, that shows base capabilities of the library.

Let's create a schedule, that means `10:00 - 19:00 from Monday to Thursday and
10:00 - 16:00 in Friday`::

   >>> import datetime as dt
   >>> from tempo.recurrenteventset import RecurrentEventSet
   >>> recurrenteventset = RecurrentEventSet.from_json(
   ...     ('OR',
   ...         ('AND', [1, 5, 'day', 'week'], [10, 19, 'hour', 'day']),
   ...         ('AND', [5, 6, 'day', 'week'], [10, 16, 'hour', 'day']))
   ... )

Then, test if `Thursday 18:00` is included in the schedule::

   >>> d1 = dt.datetime(year=2000, month=10, day=5, hour=18)
   >>> d1.weekday()  # Thursday
   3
   >>> d1 in recurrenteventset
   True

Then, do the same thing, but for `Friday 18:00`::

   >>> d2 = dt.datetime(year=2000, month=10, day=6, hour=18)
   >>> d2.weekday()  # Friday
   4
   >>> d2 in recurrenteventset
   False

It's not included. Because our schedule includes only time
from 10:00 to 16:00 in Fridays.

We also can query for future time intervals, defined by the schedule,
starting from certain point of time::

   >>> from itertools import islice
   >>> d = dt.datetime(year=2000, month=1, day=1)
   >>> list(islice(recurrenteventset.forward(start=d), 3))
   [(datetime.datetime(2000, 1, 3, 10, 0),
     datetime.datetime(2000, 1, 3, 19, 0)),
    (datetime.datetime(2000, 1, 4, 10, 0),
     datetime.datetime(2000, 1, 4, 19, 0)),
    (datetime.datetime(2000, 1, 5, 10, 0),
     datetime.datetime(2000, 1, 5, 19, 0))]

.. _readme-schedule-model:

Schedule model
==============

Example
-------

Here is an example of how Tempo represents schedules::

    ('OR',
            ('AND', [1, 5, 'day', 'week'], [10, 19, 'hour', 'day']),
            ('AND', [5, 6, 'day', 'week'], [10, 16, 'hour', 'day'])))

It means "from Monday to Thursday between 10am and 7pm and
in Friday between 10am and 4pm".

Informal definition
-------------------

Basic building block of schedule is a recurrent event,
which is defined is such way::

    [<start time>, <end time>, <time unit>, <recurrence unit>]

`<start time>` and `<end time>` are numbers, that defines interval in
which event takes it`s place. `<time unit>` defines a unit of measurement of
time for values of the interval. And `<recurrence unit>` defines how often
the interval repeats. `<time unit>` and `<recurrence unit>` values are time
measurement units, such as 'second', 'hour', 'day', 'week', 'year', etc.
`<recurrence unit>` also can be 'null', which means, that the interval doesn't
repeats in time, it just defines two points in time, that corresponds to
start and end points of the event.

Recurrent events can be composed, using operators: union - `or`,
intersection - `and` and negation - `not`.

Alternatives
============

    - python-dateutil_
    - croniter_

.. _python-dateutil: https://labix.org/python-dateutil
.. _croniter: https://github.com/kiorky/croniter

TODO
====

1. More tests for ``RecurrentEventSet``.
2. Implement negative indexing for schedules - indexing from an end of a day
   or month, etc. It will make library able to model schedules like
   "last Friday of the month".
