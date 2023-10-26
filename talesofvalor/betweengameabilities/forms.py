from django import forms

from talesofvalor.attendance.models import Attendance

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
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # limit the skills shown to what the user has
        print(f"{kwargs}")
        self.fields['ability'].queryset = kwargs['initial']['character'].skills.filter(skill__bgs_flag=True)
        # adjust fields for different users
        if user.has_perm('players.view_any_player'):
            allowed_fields = self.fields.keys()
        else:
            allowed_fields = ("ability", "count", "question",)
        self.fields = dict([(key, val) for key, val in self.fields.items() if key in allowed_fields])

    def save(self, commit=True):
        """
        Set up the to use the current event and character if one hasn't been set
        """
        bga = super().save(commit=commit)
        # if we have both the types of origins, then update the origins here.
        """
        for origin in Origin.ORIGIN_TYPES:
            if origin[0] in self.cleaned_data:
                character.origins.remove(*character.origins.filter(type=origin[0]))
                character.origins.add(self.cleaned_data[origin[0]])
        """
        return bga
