from django import forms
from django.contrib.contenttypes.forms import generic_inlineformset_factory

from talesofvalor.rules.models import Rule

from .models import Skill, Header, HeaderSkill


INCLUDE_FOR_EDIT_HEADER = ["name", "category", "description", "cost", "hidden_flag", "open_flag"]
INCLUDE_FOR_EDIT_SKILL = ["name", "tag", "description", "single_flag", "bgs_flag", "perk_flag"]


class HeaderForm(forms.ModelForm):
    """
    Handle adding a header.

    The form will allow users to add the header and set up prerequisites.
    """

    class Media:
        js = ('js/lib/jquery.formset.js', 'js/lib/jquery-ui.min.js', )

    class Meta:
        model = Header
        fields = INCLUDE_FOR_EDIT_HEADER


class SkillForm(forms.ModelForm):
    """
    Handle adding skills.

    The form will allow users to add the skill to multiple headers at multiple
    different costs.
    """

    class Media:
        js = ('js/lib/jquery.formset.js', 'js/lib/jquery-ui.min.js', )

    class Meta:
        model = Skill
        fields = INCLUDE_FOR_EDIT_SKILL


HeaderSkillFormSet = forms.inlineformset_factory(
    Skill,
    HeaderSkill,
    fields=('header', 'cost', 'capstone_flag', 'magic_flag'),
    extra=1,
    can_delete=True
)

RuleFormSet = generic_inlineformset_factory(
    Rule,
    fields='__all__',
    extra=1,
    can_delete=True
)
