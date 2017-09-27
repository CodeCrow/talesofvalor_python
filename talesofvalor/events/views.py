"""These are views that are used for viewing and editing events.
"""
from django.views.generic.edit import CreateView, UpdateView

from .models import Event

class EventCreateView(CreateView):
    model = Event
    fields = '__all__'

class EventUpdateView(UpdateView):
    model = Event
    fields = '__all__'