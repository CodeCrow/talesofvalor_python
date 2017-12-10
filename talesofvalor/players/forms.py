from django import forms
from django.contrib.auth.models import User

from .models import Player


class UserForm(forms.ModelForm):
    """Handle main user form for the user model from django."""
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'narrow-input', 'required': 'true'}
        ), required=True
    )

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'username',
            'password',
            'password_confirm',
        ]

    def clean(self):
        """
        Clean the full form data.

        We have a confirm password here, so we have to check that it matches
        the password when we clean it.
        """

        cleaned_data = super(UserForm, self).clean()
        print "ERRORS"
        print self.errors
        print "ERRORS"

        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm:
            if password != password_confirm:
                msg = "The two password fields must match."
                self.add_error('password_confirm', msg)
        return cleaned_data

class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = []

    def clean(self):
        cleaned_data = super(PlayerForm, self).clean()
        print "ERRORS"
        print self.errors
        print "ERRORS"

class RegistrationForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    email = forms.EmailField()
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        """
        Clean the full form data.

        We have a confirm password here, so we have to check that it matches
        the password when we clean it.
        """

        cleaned_data = super(RegistrationForm, self).clean()
        print "ERRORS"
        print self.errors
        print "ERRORS"

        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm:
            if password != password_confirm:
                msg = "The two password fields must match."
                self.add_error('password_confirm', msg)
        return cleaned_data
