# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import tempo.django.fields


class Migration(migrations.Migration):

    dependencies = [
        ('anapp', '0002_nullablemodel'),
    ]

    operations = [
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=99, verbose_name=b'Name')),
                ('schedule', tempo.django.fields.RecurrentEventSetField(verbose_name=b'Schedule')),
            ],
        ),
    ]
