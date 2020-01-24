''' This handles creating the form for adding skills to an origin. '''
from django import forms

from talesofvalor.skills.models import Skill

class OriginAddSkillForm(forms.Form):
    skill = forms.ModelChoiceField(
        queryset=Skill.objects.all()
    )
    count = forms.IntegerField(min_value=0)
