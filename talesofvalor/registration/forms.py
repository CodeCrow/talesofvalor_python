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
