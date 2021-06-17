"""These are views that are used for viewing and editing events."""
from django.contrib.auth.mixins import LoginRequiredMixin,\
    PermissionRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView
from django.views.generic.base import RedirectView, TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView,\
    FormMixin


from talesofvalor.attendance.models import Attendance
from talesofvalor.players.models import RegistrationRequest

from .forms import EventForm
from .models import Event, EventRegistrationItem, EVENT_MEALPLAN_PRICE

from talesofvalor.registration.forms import EventRegistrationForm


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


class PlayerRegistrationRedirectView(LoginRequiredMixin, RedirectView):
    """
    Redirect to the registration view of the next event.
    """

    pattern_name = 'events:register'

    def get_redirect_url(self, *args, **kwargs):
        """
        Figure out where the user should be redirected to if they want to
        register for the next game.
        """
        try: 
            kwargs['pk'] = Event.next_event().id
        except AttributeError:
            return reverse("events:event_no_next_event")
        return super().get_redirect_url(*args, **kwargs)

class PlayerRegistrationNoEventView(TemplateView):
    """
    Redirect to the registration view of the next event.
    """
    template_name = 'events/registration_no_scheduled_event.html'

class PlayerRegistrationView(
        LoginRequiredMixin,
        FormMixin,
        DetailView
        ):
    """
    Deals with a player signing up for an event.
    """
    model = Event
    form_class = EventRegistrationForm
    success_url = reverse_lazy('registration:create')
    template_name = 'events/registration_form.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        # Get the Event Registration Items that have an event in the
        # current year.
        context['event_items'] = EventRegistrationItem.objects.filter(
            events__event_date__year=self.object.event_date.year,
        ).distinct()
        # The price for the mealplan.
        # TODO: make this part of an event, with a default.
        context['mealplan_price'] = EVENT_MEALPLAN_PRICE
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            print(form.errors)
            return self.form_invalid(form)

    def form_valid(self, form):
        """
        The form is valid, create the event registration request
        and resend the user to the paypal screen
        """
        cleaned_data = form.cleaned_data
        # Get the registartion item to create the request.
        registration_request = RegistrationRequest.objects.create(
            event_registration_item=cleaned_data['event_registration_item'],
            mealplan_flag=cleaned_data['mealplan_flag'],
            vehicle_make=cleaned_data['vehicle_make'],
            vehicle_model=cleaned_data['vehicle_model'],
            vehicle_color=cleaned_data['vehicle_color'],
            vehicle_registration=cleaned_data['vehicle_registration'],
            local_contact=cleaned_data['local_contact'],
            notes=cleaned_data['notes'],
            player=self.request.user.player
        )
        registration_request.save()

        return super().form_valid(form)


from django.views.generic.base import RedirectView


class EventRegistrationItemListView(PermissionRequiredMixin, ListView):
    model = EventRegistrationItem
    permission_required = ('events.change_eventregistrationitem', )


class EventRegistrationItemCreateView(PermissionRequiredMixin, CreateView):
    model = EventRegistrationItem
    fields = '__all__'
    permission_required = ('events.add_eventregistrationitem', )


class EventRegistrationItemUpdateView(PermissionRequiredMixin, UpdateView):
    model = EventRegistrationItem
    fields = '__all__'
    permission_required = ('events.change_eventregistrationitem', )

