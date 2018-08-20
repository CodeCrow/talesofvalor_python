from django import forms

from talesofvalor.skill.models import Skills

class ContactForm(forms.Form):
	skill = forms.ModelChoiceField(
			queryset=Skills.object.all()
		)
    count = forms.Integer(min_value=0)