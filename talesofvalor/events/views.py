"""These are views that are used for viewing and editing events."""
from django.views.generic.edit import CreateView, UpdateView

from .forms import EventForm
from .models import Event

class EventCreateView(CreateView):
    model = Event
    form_class = EventForm

class EventUpdateView(UpdateView):
    model = Event
    form_class = EventForm