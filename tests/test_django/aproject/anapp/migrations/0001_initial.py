# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tempo.django.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('schedule', tempo.django.fields.ScheduleSetField(verbose_name=b'Schedule')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
