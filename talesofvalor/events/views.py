"""These are views that are used for viewing and editing events."""
from django.contrib.auth.mixins import LoginRequiredMixin,\
    PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView,\
    FormMixin


from talesofvalor.attendance.models import Attendance
from talesofvalor.players.models import RegistrationRequest

from .forms import EventForm, EventRegistrationForm
from .models import Event, EventRegistrationItem


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
    form_class = EventRegistrationForm
    success_url = reverse_lazy('players:player_redirect_detail')
    template_name = 'events/registration_form.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        # Get the Event Registration Items that have an event in the
        # current year.
        context['event_items'] = EventRegistrationItem.objects.filter(
            events__event_date__year=self.object.event_date.year
        ).distinct()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        """
        The form is valid, create the event registration request
        and resend the user to the paypal screen
        """
        cleaned_data = form.cleaned_data
        print(cleaned_data)
        # Get the registartion item to create the request.
        registration_item = EventRegistrationItem.objects.get(pk=cleaned_data['event_registration_item'])
        print("REGISTRATION_ITEM:{}".format(registration_item))
        registration_request = RegistrationRequest.objects.create(
            event_registration_item=registration_item,
            mealplan_flag=cleaned_data['add_meal_plan'],
            car_registration=cleaned_data['car_registration']
        )
        return super().form_valid(form)
