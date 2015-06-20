#!/usr/bin/env python
# coding=utf-8
from decimal import Decimal

from django.utils.translation import ugettext_lazy as _
from django.forms.fields import Field, ValidationError

from tempo.django.widgets import ScheduleSetWidget
from tempo.schedule import Schedule
from tempo.scheduleset import ScheduleSet


class ScheduleSetField(Field):
    widget = ScheduleSetWidget

    def to_python(self, value):
        if value is None:
            return None

        repeats = value['repeats']

        if repeats == 'monthly':
            return ScheduleSet(include=[
                Schedule(days=[int(value['repeatOn'])])
            ])
        elif repeats == 'weekly':
            schedules = []
            for repeat_on in value['repeatOn']:
                if Decimal(repeat_on['from']) > Decimal(repeat_on['to']):
                    raise ValidationError(_('"From" is greater than "to".'),
                                          code='invalid')

                schedule = Schedule(
                    weekdays=[int(repeat_on['weekday'])],
                    days=[],
                    seconds_of_the_day=list(range(
                        int(Decimal(str(repeat_on['from'])) * 60 * 60),
                        int(Decimal(str(repeat_on['to'])) * 60 * 60) + 1)
                    ),
                    seconds=[], minutes=[], hours=[]
                )
                schedules.append(schedule)

            return ScheduleSet(include=schedules)
        else:
            raise ValueError
