from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum

from talesofvalor.attendance.models import Attendance
from talesofvalor.characters.models import Character
from talesofvalor.skills.models import HeaderSkill

from .models import BetweenGameAbility


class BetweenGameAbilityForm(forms.ModelForm):
    class Meta:
        model = BetweenGameAbility
        fields = (
            "ability",
            "count",
            "question",
            "event", 
            "character",
        )

    def __init__(self, *args, **kwargs):
        """
        use this to set up the different origins
        """
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # limit the skills shown to what the user has
        character = kwargs['initial'].get('character')
        if not character:
            try:
                character = self.instance.character
            except ObjectDoesNotExist:
                pass
        if self.user.has_perm('players.change_any_player'):
            self.fields['ability'].queryset = HeaderSkill.objects.filter(skill__bgs_flag=True)
        else:
            self.fields['ability'].queryset = character.skills.filter(skill__bgs_flag=True)
        # adjust fields for different users
        if self.user.has_perm('players.change_any_player'):
            allowed_fields = self.fields.keys()
        else:
            allowed_fields = ("ability", "count", "question",)
        self.fields = dict([(key, val) for key, val in self.fields.items() if key in allowed_fields])

    def clean(self):
        """
        Make sure the player isn't asking for more than they have purchased.
        """

        cleaned_data = super().clean()
        if self.user.has_perm('players.change_any_player'):
            return cleaned_data
        character = cleaned_data.get("character")
        if not character:
            character = self.initial['character']
        character = Character.objects.get(pk=character)
        event = cleaned_data.get("event")
        if not event:
            event = self.initial['event']
        # Testing the character having the right number of purchases.
        all_skill_bgas_count = self._meta.model.objects.filter(
            event=event,
            character=character, 
            created_by=character.player
        ).exclude(pk=self.instance.id).aggregate(Sum('count'))['count__sum']
        all_skill_bgas_count = all_skill_bgas_count if all_skill_bgas_count else 0
        character_amount = character.characterskills_set.get(skill=cleaned_data.get('ability')).count
        if (cleaned_data.get('count', 0) + all_skill_bgas_count) > character_amount:
            self.add_error('count', "Requested more abilities than you have available . . .")
        # Testing attendence at previous event.
        attended_event = character.attendance_set.filter(event=event).exists()
        if not attended_event:
            self.add_error('event', "Did not attend chosen event.")
        return cleaned_data

    def save(self, commit=True):
        """
        Set up the to use the current event and character if one hasn't been set
        """
        if not self.cleaned_data.get('character'):
            if not self.instance.pk:
                self.instance.character = self.initial['character']
        if not self.cleaned_data.get('event'):
            if not self.instance.pk:
                self.instance.event = self.initial['event']
        return super().save(commit=commit)


class BetweenGameAbilityAnswerForm(forms.ModelForm):
    class Meta:
        model = BetweenGameAbility
        fields = (
            "assigned_to",
            "answer",
        )