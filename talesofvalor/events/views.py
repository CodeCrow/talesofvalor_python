"""These are views that are used for viewing and editing events."""

from datetime import date, datetime

from django.contrib.auth.mixins import LoginRequiredMixin,\
    PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.conf import settings
from django.core.mail import EmailMessage
from django.db.models import Max
from django.db.models.functions import ExtractYear
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView
from django.views.generic.base import RedirectView, TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView,\
    FormMixin, UpdateView

from talesofvalor.attendance.models import Attendance
from talesofvalor.characters.models import Character
from talesofvalor.players.models import RegistrationRequest,\
    Registration,\
    DENIED, CAST
from talesofvalor.registration.forms import CastRegistrationForm

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

    def get_context_data(self, **kwargs):
        """
        See if the user has a registration request or registration in the
        in the database.

        This allows us to update the URL at the top of the detail page to help
        players understand where they are.
        """
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            context['existing_registration'] = Registration.objects.filter(
                event=kwargs.get('object'),
                player=self.request.user.player
            ).last()
            context['existing_registration_request'] = RegistrationRequest.objects.filter(
                event_registration_item__events=kwargs.get('object'),
                player=self.request.user.player,
            ).exclude(
                status=DENIED
            ).last()
        else:
            context['existing_registration'] = None
            context['existing_registration_request'] = None
        return context


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
        existing_registration_request = RegistrationRequest.objects.filter(
            event_registration_item__events__id=kwargs['pk'],
            player=request.user.player,
        ).exclude(
            status=DENIED
        ).last()
        
        if existing_registration:
            # if you have already registered, go to edit the registration
            return HttpResponseRedirect(
                reverse('registration:detail', kwargs={'pk': existing_registration.id})
            )
        elif existing_registration_request:
            # if there is already a registration request,
            # go to edit the registration request
            return HttpResponseRedirect(
                reverse('registration:request_detail', kwargs={'pk': existing_registration_request.id})
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


class CastRegistrationRedirectView(LoginRequiredMixin, RedirectView):
    """
    Redirect to the registration view of the next event.
    """

    pattern_name = 'events:register_cast'

    def get_redirect_url(self, *args, **kwargs):
        """
        Figure out where the user should be redirected to if they want to
        register for the next game as cast.
        """
        try: 
            kwargs['pk'] = Event.next_event().id
        except AttributeError:
            return reverse("events:event_no_next_event")
        return super().get_redirect_url(*args, **kwargs)


class CastRegistrationView(
        PermissionRequiredMixin,
        CreateView
        ):
    """
    Deals with a player signing up for an event.
    """
    model = Registration
    form_class = CastRegistrationForm
    template_name = 'events/registration_cast_form.html'
    permission_required = ("players.register_as_cast",)

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
        context = super().get_context_data(**self.kwargs)
        # Get the Event Registration Items that have an event in the
        # current year, and that are still available
        context['event'] = Event.objects.get(pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        """
        The form is valid, create the event registration request
        and resend the user to the paypal screen
        """
        cleaned_data = form.cleaned_data
        # set:
        # event
        # mealplan (cast get it automatically)
        # cabin to the previous cabin
        # payment type to already paid
        # registration_type to cast
        form.instance.event = Event.objects.get(pk=self.kwargs['pk'])
        form.instance.mealplan_flag = True
        form.instance.player = self.request.user.player
        form.instance.registration_type = CAST

        response = super().form_valid(form)
 
        # send an email to staff with a link to the registration
        # send email using the self.cleaned_data dictionary
        message = """
        Hello!

        {} {} has a new registration for event {}.

        See it here:
        {}

        --ToV MechCrow
        """.format(
                self.request.user.first_name,
                self.request.user.last_name,
                form.instance.event.name,
                self.request.build_absolute_uri(
                    reverse("registration:detail", kwargs={
                        'pk': form.instance.id
                    })
                )
            )
        email_message = EmailMessage(
            "CAST Registration for {} {}".format(
                self.request.user.first_name,
                self.request.user.last_name
            ),
            message,
            settings.DEFAULT_FROM_EMAIL,
            ["rob@crowbringsdaylight.com", "wyldharrt@gmail.com", "ambisinister@gmail.com"]
        )
        # send an email to each of them.
        email_message.send()

        return response

    def get_success_url(self):
        return reverse(
            'registration:detail',
            kwargs={'pk': self.object.pk}
        )  

class EventRegistrationItemDetailView(DetailView):
    model = EventRegistrationItem


class EventRegistrationItemListView(PermissionRequiredMixin, ListView):
    model = EventRegistrationItem
    permission_required = ('events.change_eventregistrationitem', )
    paginate_by = 10  # if pagination is desired

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.GET.get('year'):
            queryset = queryset.filter(events__event_date__year=self.request.GET.get('year'))
        queryset = queryset.annotate(max_date=Max('events__event_date')).order_by('-max_date')
        
        return queryset

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['years'] = set(
            Event.objects
            .annotate(year=ExtractYear('event_date'))
            .values_list('year', flat=True)
        )
        return context_data


class EventRegistrationItemCreateView(PermissionRequiredMixin, CreateView):
    model = EventRegistrationItem
    fields = '__all__'
    permission_required = ('events.add_eventregistrationitem', )


class EventRegistrationItemUpdateView(PermissionRequiredMixin, UpdateView):
    model = EventRegistrationItem
    fields = '__all__'
    permission_required = ('events.change_eventregistrationitem', )
