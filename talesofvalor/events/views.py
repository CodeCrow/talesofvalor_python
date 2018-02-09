"""These are views that are used for viewing and editing events."""
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView


from .forms import EventForm
from .models import Event


class EventCreateView(PermissionRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    permission_required = ('events.add_event', )

class EventUpdateView(PermissionRequiredMixin, UpdateView):
    model = Event
    form_class = EventForm
    permission_required = ('events.change_event', )

class EventListView(ListView):
    model = Event

class EventDetailView(DetailView):
    model = Event
