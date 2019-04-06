from django import forms
from django.conf import settings
from django.core import mail
from django.contrib.auth.models import User
from django.db.models.query import QuerySet
from django.utils.translation import ugettext as _

from talesofvalor.characters.models import Character
from talesofvalor.events.models import Event

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


class MassRegistrationForm(forms.Form):
    """
    Allow an event to be selected and mark users as registered for it.

    Assumes that we are using the players that are selected in the session.
    """
    event_registered = forms.ModelChoiceField(
            label='',
            queryset=Event.objects.all(),
            initial=Event.next_event,
            empty_label=None
        )


class MassAttendanceForm(forms.Form):
    """
    Allow an event to be selected and mark users as attended at it.

    Assumes that we are using the players that are selected in the session.
    """
    event_attended = forms.ModelChoiceField(
            label='',
            queryset=Event.objects.all(),
            initial=Event.next_event,
            empty_label=None
        )


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


class MassGrantCPForm(forms.Form):
    """
    Grant CP to a selected list of players.

    Use this form to grant 'Amount' of CP for 'Reason' to the
    players who have been selected form the list
    """
    amount = forms.IntegerField()
    reason = forms.CharField(widget=forms.Textarea)


class TransferCPForm(forms.Form):
    """
    Transfer CP from a player to a specific character.

    Players have the pool of CP that the chracters draw from.
    Those CP say with that character and is available to them
    to buy various attributes, skills, etc.
    """
    amount = forms.IntegerField()
    character = forms.ModelChoiceField(
            label='',
            queryset=Character.objects.none(),
            empty_label=None
        )

    def __init__(self, *args, **kwargs):
        self.player = kwargs.pop('player', None)
        super(TransferCPForm, self).__init__(*args, **kwargs)
        self.fields['character'].queryset = self.player.character_set.all()

    def clean_amount(self):
        """
        Make sure there are enough points available.

        Players must have enough 'cp_available' to transfer to characters.
        """
        transfer_cps = self.cleaned_data['amount']
        if transfer_cps > self.player.cp_available:
            raise forms.ValidationError(
                _('Not enough CP available: %(value)s'),
                code='invalid',
                params={'value': transfer_cps},
                )
        return transfer_cps
