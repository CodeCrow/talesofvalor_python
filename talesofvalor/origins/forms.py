from django.contrib.contenttypes.forms import generic_inlineformset_factory

from talesofvalor.rules.models import Rule

RuleFormSet = generic_inlineformset_factory(
    Rule,
    fields='__all__',
    extra=1,
    can_delete=True
)
