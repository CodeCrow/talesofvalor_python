from django import forms
from django.contrib.contenttypes.forms import generic_inlineformset_factory

from talesofvalor.rules.models import Rule
from .models import Origin

INCLUDE_FOR_EDIT = ["name", "type", "description"]


class OriginForm(forms.ModelForm):
    """
    Handle adding Origins.

    """

    class Media:
        js = ('js/lib/jquery.formset.js', 'js/lib/jquery-ui.min.js', )

    class Meta:
        model = Origin
        fields = INCLUDE_FOR_EDIT


RuleFormSet = generic_inlineformset_factory(
    Rule,
    fields='__all__',
    extra=1,
    can_delete=True
)
