=====
Tempo
=====

.. image:: https://travis-ci.org/AndrewPashkin/python-tempo.svg?branch=master
   :alt: Build Status
   :target: https://travis-ci.org/AndrewPashkin/python-tempo

.. image:: https://coveralls.io/repos/AndrewPashkin/python-tempo/badge.svg?branch=master&service=github
   :alt: Coverage
   :target: https://coveralls.io/github/AndrewPashkin/python-tempo?branch=master

This project provides a generic way to compose and query schedules of
recurrent continuous events, such as working time of organizations, meetings,
movie shows, etc.

This repository contains a Python implementation and bindings for PostgreSQL,
Django and Django REST Framework.

Schedule model
==============

Example
-------

Here is an example of how Tempo represents schedules::

    (and [1, 6, 'day', 'week'], [10, 19, 'hour', 'day']
        (and [5, 6, 'day', 'week'], [10, 16, 'hour', 'day']))

It means "from monday to thursday between 10am and 7pm and
in friday between 10am and 4pm".

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
