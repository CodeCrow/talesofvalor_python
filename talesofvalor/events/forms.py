from datetime import date

from django import forms
from django.forms import widgets, inlineformset_factory

from talesofvalor.characters.models import CharacterEventInfluence

from .models import Event


class InfluenceInputForm(forms.ModelForm):
    """
    One row of the influence entry grid.

    Only the input is editable; the start and end are worked out when the
    event is processed.
    """

    class Meta:
        model = CharacterEventInfluence
        fields = ('influence_input', 'notes')
        widgets = {
            'influence_input': widgets.NumberInput(attrs={
                'class': 'form-control influence-value',
                'min': 0,
            }),
            'notes': widgets.TextInput(attrs={'class': 'form-control'}),
        }


InfluenceInputFormSet = inlineformset_factory(
    Event,
    CharacterEventInfluence,
    form=InfluenceInputForm,
    extra=0,
    can_delete=False
)


class EventInfluenceConfirmForm(forms.Form):
    """
    Friction in front of processing or reversing an event.

    Both of these move everybody's influence at once, so they shouldn't
    happen from a stray click.
    """
    confirm = forms.BooleanField(
        label="Yes, I'm sure",
        required=True
    )


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

