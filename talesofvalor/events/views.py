"""These are views that are used for viewing and editing events."""

from datetime import date, datetime

from django.contrib.auth.mixins import LoginRequiredMixin,\
    PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.db.models import Max
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView
from django.views.generic.base import RedirectView, TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView,\
    FormMixin

from talesofvalor.attendance.models import Attendance
from talesofvalor.characters.models import Character
from talesofvalor.players.models import RegistrationRequest,\
    Registration

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
        qs = super().get_queryset()
        character_id = self.kwargs.get('character', None)
        if character_id:
            attendances = Attendance.objects\
                .filter(character=self.kwargs['character'])\
                .values_list('id', flat=True)
            qs = qs.filter(id__in=attendances)
        # if there is a next event start the list there
        next_event = Event.next_event()
        if next_event:
            qs = qs.filter(event_date__gte=next_event.event_date)
        return qs


class EventPastListView(ListView):
    model = Event
    template_name = 'events/event_past_list.html'

    def get_queryset(self):
        """
        Limit the events.

        We might only want events that a particular character attended.
        """
        qs = super().get_queryset().filter(event_date__lte=date.today())\
            .order_by('-event_date')
        return qs


class EventDetailView(DetailView):
    model = Event


class EventCharacterPrintListView(PermissionRequiredMixin, ListView):
    """
    Show the list of characters for an event.

    """
    model = Character
    permission_required = ('player.can_update_any_player',)
    template_name = "events/event)character_print.html"


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

    def dispatch(self, request, *args, **kwargs):
        """
        Make sure that the user hasn't already registered for this event.
        """
        existing_registration = Registration.objects.filter(event__id=kwargs['pk'], player=request.user.player).last()
        if existing_registration:
            # if you have already registered, go to edit the registration
            return HttpResponseRedirect(
                reverse('registration:detail', kwargs={'pk': existing_registration.id})
            )
        else:
            return super().dispatch(request, args, kwargs)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        # Get the Event Registration Items that have an event in the
        # current year, and that are still available
        context['event_items'] = EventRegistrationItem.objects.filter(
            available=True,
            events__event_date__year=self.object.event_date.year,
            events__event_date__gte=datetime.now()
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
            vegetarian_flag=cleaned_data['vegetarian_flag'],
            vegan_flag=cleaned_data['vegan_flag'],
            food_allergies=cleaned_data['food_allergies'],
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


class EventRegistrationItemDetailView(DetailView):
    model = EventRegistrationItem


class EventRegistrationItemListView(PermissionRequiredMixin, ListView):
    model = EventRegistrationItem
    permission_required = ('events.change_eventregistrationitem', )
    paginate_by = 10  # if pagination is desired

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset.annotate(max_date=Max('events')).order_by('max_date')
        return queryset


class EventRegistrationItemCreateView(PermissionRequiredMixin, CreateView):
    model = EventRegistrationItem
    fields = '__all__'
    permission_required = ('events.add_eventregistrationitem', )


class EventRegistrationItemUpdateView(PermissionRequiredMixin, UpdateView):
    model = EventRegistrationItem
    fields = '__all__'
    permission_required = ('events.change_eventregistrationitem', )
