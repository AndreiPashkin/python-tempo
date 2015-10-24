from django.db import models
from tempo.django.fields import RecurrentEventSetField


class AModel(models.Model):
    schedule = RecurrentEventSetField("Schedule")


class NullableModel(models.Model):
    schedule = RecurrentEventSetField("Schedule", null=True, blank=True)


class Movie(models.Model):
    name = models.CharField('Name', max_length=99)
    schedule = RecurrentEventSetField('Schedule')

    __str__ = __unicode__ = lambda self: self.name
