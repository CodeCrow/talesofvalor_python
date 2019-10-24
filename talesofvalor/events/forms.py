from django import forms

from .models import Event


class EventForm(forms.ModelForm):
    """
    Show the form for entering events.

    We need a form for entering events rather than just using that provided
    by the generic view (in events/views.py) because we have to add
    the datepicker.
    """
    class Meta:
        """Set up the attributes for the event form."""
        model = Event
        fields = '__all__'
        widgets = {
            'event_date': forms.DateInput(attrs={'class': 'datepicker'}),
            'pel_due_date': forms.DateInput(attrs={'class': 'datepicker'}),
            'bgs_due_date': forms.DateInput(attrs={'class': 'datepicker'})
        }

    class Media:
        """Add the media so that the datepicker will work."""
        css = {
            'all': ('css/lib/jquery-ui.css',)
        }
        js = ('js/lib/jquery-ui.min.js', )

class EventRegistrationForm(forms.Form):
    """
    Register for some event or events.
    """
    event_registration_item = forms.IntegerField()
    add_meal_plan = forms.BooleanField(required=False)
    vehicle_make = forms.CharField(required=False)
    vehicle_model = forms.CharField(required=False)
    vehicle_color = forms.CharField(required=False)
    vehicle_registration = forms.CharField(required=False)
    local_contact = forms.CharField(required=False)
    notes = forms.CharField(widget=forms.Textarea, required=False)
