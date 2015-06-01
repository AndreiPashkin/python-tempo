from django.db import models
from tempo.django.fields import ScheduleSetField


class AModel(models.Model):
    schedule = ScheduleSetField("Schedule")
