from django import forms
from django.forms import widgets

from .models import Character


class CharacterForm(forms.ModelForm):
    class Meta:
        model = Character
        exclude = [
            'headers',
            'skills',
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

        We have to break down the student list that was sent so that we can
        indicate what the valid choices are.
        """
        # do pop first, so the parent doesn't get unexpected arguments.
        skills = kwargs.pop('skills')
        super(CharacterSkillForm, self).__init__(*args, **kwargs)
        self.fields['skills'].choices = \
            [(s.id, s.name)
                for header in skills
                for s in header.skills.all()]
        self.fields['headers'].choices = \
            [(h.id, h.name) for h in skills]

