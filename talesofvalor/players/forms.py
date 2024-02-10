from django import forms
from django.conf import settings
from django.core import mail
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db.models.query import QuerySet
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from talesofvalor.characters.models import POINT_CAP, Character
from talesofvalor.events.models import Event

from .models import Player, PEL


class UserForm(forms.ModelForm):
    """Handle main user form for the user model from django.
    This also has access to groups, which players shouldn't have access to."""
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
            'groups',
        ]


    def clean(self):
        """
        Clean the full form data.

        We have a confirm password here, so we have to check that it matches
        the password when we clean it.
        """

        cleaned_data = super(UserForm, self).clean()
        print("ERRORS")
        print(self.errors)
        print("ERRORS")

        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm:
            if password != password_confirm:
                msg = "The two password fields must match."
                self.add_error('password_confirm', msg)
        return cleaned_data


class PlayerViewable_UserForm(UserForm):
    """Handle main user form for the user model from django.
    This is the base class intended for players."""
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email',
        ]


class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = [
            'game_started',
            'cp_available',
            'staff_attention_flag',
            'player_pronouns',
            'food_allergies'
        ]


class PlayerViewable_PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = [
            'player_pronouns',
            'food_allergies'
        ]


class RegistrationForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    player_pronouns = forms.CharField(max_length=25, required=False)
    food_allergies = forms.CharField(widget=forms.Textarea, required=False)

    email = forms.EmailField()
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)

    def clean_email(self):
        """
        Make sure the email is unique
        """
        data = self.cleaned_data['email']
        if User.objects.filter(email=data).exists():
            raise ValidationError(mark_safe(f"This email address already exists.  Did you <a href=\"{reverse('password_reset')}\">forget your login?</a>"))

        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return data

    def clean_username(self):
        """
        The username should be unique
        """
        data = self.cleaned_data['username']
        if User.objects.filter(username=data).exists():
            raise ValidationError(mark_safe(f"This username already exists.  Did you <a href=\"{reverse('password_reset')}\">forget your login?</a>"))


        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return data

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

    def clean(self):
        """
        Make sure the user isn't breaking their season cap

        the cp_transfered must end up being less than the season cap.
        """
        cleaned_data = super().clean()
        character_target = cleaned_data['character']
        transfer_cps = cleaned_data.get('amount', int(self.data.get('amount', 0)))
        if transfer_cps + character_target.cp_transferred > POINT_CAP:
            raise forms.ValidationError(
                _('Transfer %(value)s is more than available Point Cap %(cap)s.'),
                code='invalid',
                params={
                    'value': transfer_cps,
                    'cap': POINT_CAP
                    },
                )


class PELUpdateForm(forms.ModelForm):
    return_url = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        '''
        set up how to return based on where you came from
        '''
        self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)
        self.return_url = self.request.META['HTTP_REFERER']
        self.fields['return_url'].initial = self.return_url

    class Meta:
        model = PEL
        fields = '__all__'
        events = ['event']

        # We want all fields to be 80 cols wide, but rows are either 3 or 5.
        widgets = {
            'player': forms.HiddenInput(),
            'event': forms.HiddenInput(),
            'donations_time': forms.Textarea(attrs={'cols': '80', 'rows': '3'}),
            'donations_props': forms.Textarea(attrs={'cols': '80', 'rows': '3'}),
            'favorites': forms.Textarea(attrs={'cols': '80', 'rows': '5'}),
            'suggestions': forms.Textarea(attrs={'cols': '80', 'rows': '5'}),
            'plans': forms.Textarea(attrs={'cols': '80', 'rows': '5'}),
            'devout': forms.Textarea(attrs={'cols': '80', 'rows': '3'}),
            'new_rule_likes': forms.Textarea(attrs={'cols': '80', 'rows': '3'}),
            'new_rule_dislikes': forms.Textarea(attrs={'cols': '80', 'rows': '3'}),
            'learned': forms.Textarea(attrs={'cols': '80', 'rows': '3'}),
        }
