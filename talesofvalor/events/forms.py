from django.forms import ModelForm, DateInput

from .models import Event

class EventForm(ModelForm):
    class Meta:
        model = Event
        fields = '__all__'
        widgets = {
            'event_date': DateInput(attrs={'class': 'datepicker'}),
            'pel_due_date': DateInput(attrs={'class': 'datepicker'}),
            'bgs_due_date': DateInput(attrs={'class': 'datepicker'})
        }
    class Media: 
        css = {
            'all': ('css/lib/jquery-ui.css',)
        }
        js = ('js/lib/jquery-ui.min.js', )