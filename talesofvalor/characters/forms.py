from django import forms
from django.core.exceptions import ValidationError
from django.forms import widgets

from talesofvalor.origins.models import Origin
from .models import Character


PLAYER_ALLOWED_FIELDS = [
    'name',
    'pronouns',
    'description',
    'history',
    'picture',
    'player_notes'
]
NEW_PLAYER_FIELDS = [
    'tradition',
    'people'
]


class CharacterForm(forms.ModelForm):
    tradition = forms.ModelChoiceField(
        queryset=Origin.objects.filter(type=Origin.TRADITION),
    )
    people = forms.ModelChoiceField(
        queryset=Origin.objects.filter(type=Origin.PEOPLE),
    )

    def __init__(self, *args, **kwargs):
        """
        use this to set up the different origins
        """
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.instance.id:
            for origin in Origin.ORIGIN_TYPES:
                # in case they had an origin that doesn't exist any more.
                try:
                    self.fields[origin[0]].initial = self.instance.origins.filter(type=origin[0]).first()
                except Origin.DoesNotExist:
                    pass
        # adjust fields for different users
        if user.has_perm('players.view_any_player'):
            allowed_fields = self.fields.keys()
        else:
            allowed_fields = PLAYER_ALLOWED_FIELDS
            if not self.instance.id:
                allowed_fields = allowed_fields + NEW_PLAYER_FIELDS
        self.fields = dict([(key, val) for key, val in self.fields.items() if key in allowed_fields])

    def save(self, commit=True):
        character = super().save(commit=commit)
        # if we have both the types of origins, then update the origins here.
        for origin in Origin.ORIGIN_TYPES:
            if origin[0] in self.cleaned_data:
                character.origins.remove(*character.origins.filter(type=origin[0]))
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


class CharacterConceptApproveForm(forms.Form):
    """
    Form indicating approval of a characters history
    """
    character_id = forms.IntegerField()

    def clean(self):
        """
        Make sure the hisotry hasn't already been approved.
        """
        character_id = self.cleaned_data['character_id']
        character = Character.objects.get(pk=character_id)
        if character.concept_approved_flag:
            raise ValidationError(f"The concept for {character} has already been approved.")
        return super().clean()


class CharacterHistoryApproveForm(forms.Form):
    """
    Form indicating approval of a characters history
    """
    character_id = forms.IntegerField()

    def clean(self):
        """
        Make sure the hisotry hasn't already been approved.
        """
        character_id = self.cleaned_data['character_id']
        character = Character.objects.get(pk=character_id)
        if character.history_approved_flag:
            raise ValidationError(f"The history for {character} has already been approved.")
        return super().clean()



