from django.db import models
from tempo.django.fields import RecurrentEventSetField


class AModel(models.Model):
    schedule = RecurrentEventSetField("Schedule")


class NullableModel(models.Model):
    schedule = RecurrentEventSetField("Schedule", null=True, blank=True)
