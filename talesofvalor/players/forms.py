from django import forms
from django.conf import settings
from django.core import mail
from django.contrib.auth.models import User
from django.db.models.query import QuerySet

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
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm:
            if password != password_confirm:
                msg = "The two password fields must match."
                self.add_error('password_confirm', msg)
        return cleaned_data


class MassEmailForm(forms.Form):
    """
    The form that is used to send out a mass email based
    on selected Players
    """
    subject = forms.CharField()
    message = forms.CharField(widget=forms.Textarea)

    def send_email(self, players):
        """
        send an email message to 'players'

        'players' can be a single user.
        """
        # is it s single player, or multiple:
        if not(isinstance(players, QuerySet)):
            players = [players, ]
        # send email using the self.cleaned_data dictionary
        email_connection = mail.get_connection()
        # create the list of messages
        email_messages = []
        for player in players:
            email_message = mail.EmailMessage(
                self.cleaned_data['subject'],
                self.cleaned_data['message'],
                settings.DEFAULT_FROM_EMAIL,
                [player.user.email]
            )
            email_messages.append(email_message)
        # send an email to each of them.
        email_connection.send_messages(email_messages)
        # close the connection to the email server
        email_connection.close()
