from django.forms import ModelForm, DateInput

from .models import Event

class EventForm(ModelForm):
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
            'event_date': DateInput(attrs={'class': 'datepicker'}),
            'pel_due_date': DateInput(attrs={'class': 'datepicker'}),
            'bgs_due_date': DateInput(attrs={'class': 'datepicker'})
        }
    class Media: 
        """Add the media so that the datepicker will work."""
        css = {
            'all': ('css/lib/jquery-ui.css',)
        }
        js = ('js/lib/jquery-ui.min.js', )