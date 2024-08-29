from django import forms

from talesofvalor.players.models import Registration, RegistrationRequest


# Create the form class.
class EventRegistrationForm(forms.ModelForm):
    class Meta:
        model = RegistrationRequest
        fields = [
            'event_registration_item',
            'mealplan_flag',
            'food_allergies',
            'vegetarian_flag',
            'vegan_flag',
            'no_car_flag',
            'vehicle_make',
            'vehicle_model',
            'vehicle_color',
            'vehicle_registration',
            'site_transportation',
            'local_contact',
            'notes'
        ]

# Create the form class.
class CastRegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = [
            'food_allergies',
            'vegetarian_flag',
            'vegan_flag',
            'no_car_flag',
            'vehicle_make',
            'vehicle_model',
            'vehicle_color',
            'vehicle_registration',
            'site_transportation',
            'local_contact',
            'notes'
        ]


class RegistrationCompleteForm(forms.Form):
    """
    Handles the order request completion.

    Is should only ever be involved in reacting to a POST call.
    """
    order_id = forms.CharField()


class RegistrationRequestApproveForm(forms.Form):
    """
    Handles the registration for an an individual request.

    Is should only ever be involved in reacting to a POST call.

    We only need this because the form view requires it.
    """


class RegistrationRequestDenyForm(forms.Form):
    """
    Handles the DENYING the registration for an an individual request.

    Is should only ever be involved in reacting to a POST call.

    We only need this because the form view requires it.
    """
