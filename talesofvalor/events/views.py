"""These are views that are used for viewing and editing events."""
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView

from talesofvalor.attendance.models import Attendance

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

    def get_queryset(self):
        """
        Limit the events.

        We might only want events that a particular character attended.
        """
        qs = self.model.objects.all()
        character_id = self.kwargs.get('character', None)
        if character_id:
            attendances = Attendance.objects\
                .filter(character=self.kwargs['character'])\
                .values_list('id', flat=True)
            qs = qs.filter(id__in=attendances)
        return qs


class EventDetailView(DetailView):
    model = Event
