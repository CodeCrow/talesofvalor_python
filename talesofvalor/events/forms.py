from datetime import date

from django import forms

from .models import Event


class EventForm(forms.ModelForm):
    """
    Show the form for entering events.

    We need a form for entering events rather than just using that provided
    by the generic view (in events/views.py) because we have to add
    the datepicker.
    """
    def __init__(self, *args, **kwargs):
        '''
        set up how to return based on where you came from
        '''
        super().__init__(*args, **kwargs)
        self.fields['event_date'].initial = date.today()
        self.fields['pel_due_date'].initial = date.today()
        self.fields['bgs_due_date'].initial = date.today()

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

