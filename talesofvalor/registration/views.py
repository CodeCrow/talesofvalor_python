from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin,\
    LoginRequiredMixin, PermissionRequiredMixin
from django.core import mail
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, TemplateView, ListView, DeleteView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from paypalcheckoutsdk.orders import OrdersGetRequest

from talesofvalor.mixins import PayPalClientMixin
from talesofvalor.players.models import RegistrationRequest, Registration,\
    COMPLETE, REQUESTED

from .forms import RegistrationCompleteForm


class RegistrationSendView(PayPalClientMixin, TemplateView):
    template_name = "registration/registration_send.html"

    def dispatch(self, request, *args, **kwargs):
        """
        Make sure that the user hasn't already registered for this event.
        """
        existing_registration_request = RegistrationRequest.objects.filter(
            player=request.user.player,
            status=REQUESTED
        ).exists()
        if not existing_registration_request:

            # If there are no more requests go back to list
            messages.info(self.request, "No Registration Requests Left.  Please choose an event to register for.")
            return HttpResponseRedirect(
                reverse('events:event_list')
            )
        else:
            return super().dispatch(request, args, kwargs)

    def get_context_data(self, **kwargs):
        """
        This template should show the current pending request for the current
        user.

        It should show the current request (or indicate that there isn't one)
        and the paypal button.

        If there is no request, the paypal button should not be shown.
        """
        context_data = super().get_context_data(**kwargs)
        context_data['registration_requests'] = \
            RegistrationRequest.objects.filter(
                player=self.request.user.player,
                status=REQUESTED
            )
        context_data['PAYPAL_CLIENT_ID'] = self.client_id
        context_data['PAYPAL_CLIENT_SECRET'] = self.client_secret
        return context_data


class RegistrationCompleteView(PayPalClientMixin, FormView):
    template_name = "registration/registration_complete.html"
    form_class = RegistrationCompleteForm

    def get_success_url(self):
        """
        The form has been successful.

        Now, we want to create the success url
        """
        return reverse('registration:request_detail', kwargs={
            'pk': self.kwargs.get('registration_request_id')
        })

    def form_valid(self, form):
        """
        Getting the request and then:

        - get the order from paypal
        - Get the request
        """
        request = OrdersGetRequest(form.cleaned_data['order_id'])
        # Call PayPal to get the transaction
        response = self.client.execute(request)
        # load the registration request id from the paypal order
        self.kwargs['registration_request_id'] = response.result.purchase_units[0].custom_id
        # update the request status and add the order id
        event_reg_request = RegistrationRequest.objects.get(
            pk=self.kwargs['registration_request_id']
        )
        event_reg_request.paypal_order_id = form.cleaned_data['order_id']
        event_reg_request.status = COMPLETE
        event_reg_request.save()
        # Create the event registration for each of the events that the
        # event_reg_request.eventregistrationitem is attached to.
        # create an email message for each registration
        email_connection = mail.get_connection()
        # create the list of messages
        email_messages = []
        for event in event_reg_request.event_registration_item.events.all():
            registration = Registration(
                player=self.request.user.player,
                event=event,
                no_car_flag=event_reg_request.no_car_flag,
                site_transportation=event_reg_request.site_transportation,
                vehicle_make=event_reg_request.vehicle_make,
                vehicle_model=event_reg_request.vehicle_model,
                vehicle_color=event_reg_request.vehicle_color,
                vehicle_registration=event_reg_request.vehicle_registration,
                local_contact=event_reg_request.local_contact,
                registration_request=event_reg_request,
                mealplan_flag=event_reg_request.mealplan_flag,
                food_allergies=event_reg_request.food_allergies,
                vegetarian_flag=event_reg_request.vegetarian_flag,
                vegan_flag=event_reg_request.vegan_flag
                )
            registration.save()
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
                    event.name,
                    self.request.build_absolute_uri(
                        reverse("registration:detail", kwargs={
                            'pk': registration.id
                        })
                    )
                )
            email_message = mail.EmailMessage(
                "Registration for {} {}".format(
                    self.request.user.first_name,
                    self.request.user.last_name
                ),
                message,
                settings.DEFAULT_FROM_EMAIL,
                ["rob@crowbringsdaylight.com", "wyldharrt@gmail.com"]
            )
            email_messages.append(email_message)
        # send an email to each of them.
        email_connection.send_messages(email_messages)
        # close the connection to the email server
        email_connection.close()

        return super().form_valid(form)


class RegistrationDetailView(
        LoginRequiredMixin,
        UserPassesTestMixin,
        DetailView
        ):
    """
    Show a specific, completed registration.
    """
    template_name = "registration/registration_detail.html"
    model = Registration

    def test_func(self):
        if self.request.user.has_perm('players.view_any_player'):
            return True
        try:
            player = Registration.objects.get(pk=self.kwargs['pk']).player
            return (player.user == self.request.user)
        except Registration.DoesNotExist:
            return False
        return False


class RegistrationUpdateView(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        UpdateView
        ):
    """
    Show a specific, completed registration.
    """
    fields = (
        'cabin',
        'mealplan_flag',
        'notes',
    )
    template_name = "registration/registration_form.html"
    model = Registration
    permission_required = ('registration.change_registration', )

    def get_success_url(self):
        """
        The form has been successful.

        Now, we want to create the success url, using the origin that was
        editted.
        """
        return reverse('registration:list', kwargs={
            'event': self.object.event.id
        })


class RegistrationListView(
        LoginRequiredMixin,
        ListView
        ):
    """
    Show a specific, completed registration.
    """
    template_name = "registration/registration_list.html"
    model = Registration
    # permission_required = ('registration.add_registration', )

    def get_queryset(self):
        """
        based on the event id, get the registrations for that event.
        If we have a player id, or do not have admin permissions, we can limit
        by the player.
        """
        return self.model.objects.filter(event=self.kwargs['event'])


class RegistrationRequestDetailView(
        LoginRequiredMixin,
        DetailView
        ):
    """
    Show a request for registration, whether it is finished or not.
    """
    template_name = "registration/registrationrequest_detail.html"
    model = RegistrationRequest


class RegistrationRequestDeleteView(
        LoginRequiredMixin,
        UserPassesTestMixin,
        DeleteView
        ):
    """
    Removes a request for registration that a user has.

    This is so someone can get rid of abandoned requests.
    """
    template_name = "registration/registration_delete.html"
    model = RegistrationRequest
    success_url = reverse_lazy('registration:create')

    def test_func(self):
        if self.request.user.has_perm('players.view_any_player'):
            return True
        try:
            player = RegistrationRequest.objects.get(pk=self.kwargs['pk']).player
            return (player.user == self.request.user)
        except RegistrationRequest.DoesNotExist:
            return False
        return False
