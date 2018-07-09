from django import forms

from .models import Skill, HeaderSkill


INCLUDE_FOR_EDIT_SKILL = ["name", "tag", "description", "attention_flag", "bgs_flag"]


class SkillForm(forms.ModelForm):
    """
    Handle adding skills.

    The form will allow users to add the skill to multiple headers at multiple
    different costs.
    """
    class Meta:
        model = Skill
        fields = INCLUDE_FOR_EDIT_SKILL

HeaderSkillFormSet = forms.inlineformset_factory(
    Skill,
    HeaderSkill,
    fields=('header', 'cost', 'dabble_flag'),
    extra=1,
    can_delete=True
)
