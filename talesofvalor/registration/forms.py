from django import forms

from talesofvalor.players.models import RegistrationRequest


# Create the form class.
class EventRegistrationForm(forms.ModelForm):
    class Meta:
        model = RegistrationRequest
        fields = [
            'event_registration_item',
            'mealplan_flag',
            'vehicle_make',
            'vehicle_model',
            'vehicle_color',
            'vehicle_registration',
            'local_contact',
            'notes'
        ]


class RegistrationCompleteForm(forms.Form):
    """
    Handles the order request completion.

    Is should only ever be involved in reacting to a POST call.
    """
    order_id = forms.CharField()
