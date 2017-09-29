from django import forms
from django.contrib.auth.models import User

from .models import Player

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'

class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = '__all__'

class RegistrationForm(forms.ModelForm):

    class Meta: 
        model = Player
        fields = '__all__'