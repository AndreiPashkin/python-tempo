#!/usr/bin/env python
# coding=utf-8
from decimal import Decimal
import json
import uuid

from django.forms.utils import flatatt
from django.forms.widgets import Input


class ScheduleSetWidget(Input):
    def prepare(self, value):
        if isinstance(value, dict):
            return value
        include = list(value.include)
        if (len(include) == 1 and
            include[0] is not None and
            len(include[0].days) == 1):
            return {
                'repeats': 'monthly',
                'repeatOn': include[0].days[0]
            }
        elif all((s.days is not None and len(s.days) == 0 and
                  s.weekdays is not None and len(s.weekdays) == 1 and
                  s.seconds is not None and len(s.seconds) == 0 and
                  s.minutes is not None and len(s.minutes) == 0 and
                  s.hours is not None and len(s.hours) == 0 and
                  s.seconds_of_the_day is not None and
                  len(s.seconds_of_the_day) != 0)
                 for s in include):
            return {
                'repeats': 'weekly',
                'repeatOn': [
                    {'weekdays': s.weekdays[0],
                     'from': float(Decimal(s.seconds_of_the_day[0]) / 60 / 60),
                     'to': float(Decimal(s.seconds_of_the_day[-1] / 60 / 60))}
                    for s in include
                ]
            }
        else:
            raise ValueError

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        else:
            value = json.dumps(self.prepare(value))

        final_attrs = self.build_attrs(attrs, name=name)
        return """
        <input type='hidden' {attrs} />
        <script id={uuid}>(function($){{
            $('#{uuid}').prev().tempo({value});
        }})(django.jQuery)</script>
        """.format(uuid=str(uuid.uuid4()), attrs=flatatt(final_attrs),
                   value=value)

    def value_from_datadict(self, data, files, name):
        value = data.get(name)
        if value is None or value is '':
            return None

        return json.loads(value)

    class Media:
        css = {
            'all': ('tempo/widget.css',)
        }
        js = ('tempo/widget.js',)
