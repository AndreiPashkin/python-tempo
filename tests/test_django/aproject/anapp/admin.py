from django.contrib import admin
from django import forms

from tests.test_django.aproject.anapp.models import AModel

from tempo.django.forms import RecurrentEventSetField


class AModelAdminForm(forms.ModelForm):
    schedule = RecurrentEventSetField()

    class Meta:
        model = AModel
        fields = ['schedule']


class AModelAdmin(admin.ModelAdmin):
    form = AModelAdminForm

admin.site.register(AModel, AModelAdmin)
