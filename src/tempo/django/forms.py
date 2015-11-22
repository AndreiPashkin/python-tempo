"""Provides Django-Admin form field."""
# coding=utf-8
from django.utils.translation import ugettext_lazy as _
from django.forms.fields import Field, ValidationError

from tempo.django.widgets import RecurrentEventSetWidget
from tempo.recurrenteventset import RecurrentEventSet


class RecurrentEventSetField(Field):
    """Form field, for usage in admin forms.
    Represents RecurrentEventSet."""
    # pylint: disable=no-init
    widget = RecurrentEventSetWidget

    def clean(self, value):
        """Cleans and validates RecurrentEventSet expression."""
        # pylint: disable=no-self-use
        if value is None:
            return None
        if not RecurrentEventSet.validate_json(value):
            raise ValidationError(_('Invalid input.'),
                                  code='invalid')

        return RecurrentEventSet.from_json(value)
