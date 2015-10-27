=============
API reference
=============

Python
======

tempo.recurrentevent
--------------------
.. automodule:: tempo.recurrentevent
   :members:

tempo.recurrenteventset
-----------------------
.. automodule:: tempo.recurrenteventset
   :members:

PostgreSQL
==========

.. describe:: tempo_recurrentevent

   :TYPE: domain type
   :BASE: jsonb

   A domain type, that represents :py:class:`.RecurrentEvent`.

.. describe:: tempo_recurrenteventset

   :TYPE: domain type
   :BASE: jsonb

   A domain type, that represents :py:class:`.RecurrentEventSet`.

.. describe:: tempo_recurrenteventset_contains (recurrenteventset tempo_recurrenteventset, datetime timestamp)

   :TYPE: function
   :RETURNS: boolean
   :VOLATILITY: IMMUTABLE
   :LANGUAGE: plpythonu

   Checks `datetime` for containment in `recurrenteventset`.

.. describe:: tempo_recurrenteventset_forward (recurrenteventset tempo_recurrenteventset, start timestamp, n integer, clamp bool DEFAULT true)

   :TYPE: function
   :RETURNS: TABLE(start timestamp, stop timestamp)
   :VOLATILITY: IMMUTABLE
   :LANGUAGE: plpythonu

   Future intervals of `recurrenteventset` as set of rows.

Django
======

tempo.django.fields
-------------------
.. automodule:: tempo.django.fields
   :members:

Django-REST-Framework
=====================

tempo.rest_framework.serializers
--------------------------------
.. automodule:: tempo.rest_framework.serializers
   :members:
