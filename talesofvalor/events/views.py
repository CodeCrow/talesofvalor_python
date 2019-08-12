"""These are views that are used for viewing and editing events."""
from django.contrib.auth.mixins import LoginRequiredMixin,\
    PermissionRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView,\
    FormMixin

from paypal.standard.forms import PayPalPaymentsForm

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


class PlayerRegistrationView(
        LoginRequiredMixin,
        FormMixin,
        DetailView
        ):
    """
    Deals with a player signing up for an event.
    """
    model = Event
    success_url = reverse_lazy('players:player_redirect_detail')
    form_class = PayPalPaymentsForm
    template_name = 'events/registration_form.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Update the context with the paypal dictionary.

        context.update({
            "business": "receiver_email@example.com",
            "amount": "10000000.00",
            "item_name": "name of the item",
            "invoice": "unique-invoice-id",
            "notify_url": self.request.build_absolute_uri(
                reverse('paypal-ipn')
            ),
            '''
            "return": self.request.build_absolute_uri(
                reverse('your-return-view')
            ),
            "cancel_return": self.request.build_absolute_uri(
                reverse('your-cancel-view')
            ),
            '''
            # Custom command to correlate to some function later (optional)
            "custom": "premium_plan",
        })
        return context
