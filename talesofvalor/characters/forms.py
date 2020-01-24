from django import forms
from django.forms import widgets

from talesofvalor.origins.models import Origin
from .models import Character


class CharacterForm(forms.ModelForm):
    background = forms.ModelChoiceField(
        queryset=Origin.objects.filter(type=Origin.BACKGROUND),
    )
    race = forms.ModelChoiceField(
        queryset=Origin.objects.filter(type=Origin.RACE),
    )

    def __init__(self, *args, **kwargs):
        """
        use this to set up the different origins
        """
        super().__init__(*args, **kwargs)
        for origin in Origin.ORIGIN_TYPES:
            self.fields[origin[0]].initial = self.instance.origins.filter(type=origin[0])

    def save(self, commit=True):
        character = super().save(commit=commit)
        character.origins.clear()
        for origin in Origin.ORIGIN_TYPES:
            character.origins.add(self.cleaned_data[origin[0]])
        return character

    class Meta:
        model = Character
        exclude = [
            'headers',
            'skills',
            'origins'
         ]


class CharacterSkillForm(forms.Form):
    """
    Allow skills to be added by a player to a character.

    The context of the tmeplate should have the list of the headers
    and associated skills so we can build a good looking form.
    """
    headers = forms.TypedMultipleChoiceField(
        required=False,
        widget=widgets.CheckboxSelectMultiple(),
        coerce=int
    )
    skills = forms.TypedMultipleChoiceField(
        required=False,
        widget=widgets.CheckboxSelectMultiple(),
        coerce=int
    )

    def __init__(self, *args, **kwargs):
        """
        Initializing the form.

        We have to break down the skills list that was sent so that we can
        indicate what the valid choices are.
        """
        # do pop first, so the parent doesn't get unexpected arguments.
        skills = kwargs.pop('skills')
        super(CharacterSkillForm, self).__init__(*args, **kwargs)
        self.fields['skills'].choices = \
            [(s.id, s.skill.name)
                for header in skills
                for s in header.headerskill_set.all()]
        self.fields['headers'].choices = \
            [(h.id, h.name) for h in skills]

    def clean(self):
        """
        Check and make sure the skills that have been chosen are valid.

        This should make sure that the character has enough points for the
        purchases AND that different skills don't interact badly.

        It has to take into account Grants, dabbling and different costs
        for things like jack of all trades etc.

        We should probably make a hash/dict based on headers that stores
        the expected costs per skill.  This was how it was done previously.
        """
        return super(CharacterSkillForm, self).clean()
