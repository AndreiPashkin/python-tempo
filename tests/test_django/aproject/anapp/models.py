from django.db import models
from tempo.django.fields import TimeIntervalSetField


class AModel(models.Model):
    schedule = TimeIntervalSetField("Schedule")


class NullableModel(models.Model):
    schedule = TimeIntervalSetField("Schedule", null=True, blank=True)
