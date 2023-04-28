from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin,\
    LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic.base import RedirectView
from django.views.generic import DeleteView, FormView, ListView, TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from paypalcheckoutsdk.orders import OrdersGetRequest

from talesofvalor.mixins import PayPalClientMixin
from talesofvalor.players.models import RegistrationRequest, Registration,\
    COMPLETE, DENIED, REQUESTED

from .forms import RegistrationCompleteForm, RegistrationRequestApproveForm,\
    RegistrationRequestDenyForm


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
        
        RegistrationRequest.request_complete(
            event_reg_request.id,
            self.request.user,
            self.request
        )

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


class RegistrationRequestListView(PermissionRequiredMixin, ListView):
    '''
    List the PELs for staff memebers
    '''
    permission_required = ('players.view_any_player', )
    queryset = RegistrationRequest.objects.exclude(status__in=[COMPLETE, DENIED,])
    template_name = "registration/registrationrequest_list.html"
    paginate_by = 25  # if pagination is desired


class RegistrationRequestDetailView(
        LoginRequiredMixin,
        DetailView
        ):
    """
    Show a request for registration, whether it is finished or not.
    """
    template_name = "registration/registrationrequest_detail.html"
    model = RegistrationRequest


class RegistrationRequestAlreadyPaidView(
        LoginRequiredMixin,
        UserPassesTestMixin,
        RedirectView
        ):
    """
    Someone is indicating that they have already paid.

    This should continue the sign up so that the player is registered.

    Updates the registration request to add the already_paid_flag

    Then moves the user on to completing the registration
    """
    pattern_name = 'registration:complete'

    def test_func(self):
        if self.request.user.has_perm('players.view_any_player'):
            return True
        try:
            player = RegistrationRequest.objects.get(pk=self.kwargs['pk']).player
            return (player.user == self.request.user)
        except RegistrationRequest.DoesNotExist:
            return False
        return False

    def get_redirect_url(self, *args, **kwargs):
        # get the registration request id
        registration_request = RegistrationRequest.objects.get(pk=self.kwargs['pk'])
        # and set the correct flag.
        registration_request.already_paid_flag = True
        registration_request.save(update_fields=['already_paid_flag'])
        RegistrationRequest.request_complete(
            self.kwargs['pk'],
            self.request.user,
            self.request
        )
        del kwargs['pk']
        return super().get_redirect_url(*args, **kwargs)


class RegistrationRequestApproveFormView(
        PermissionRequiredMixin,
        FormView
        ):

    form_class = RegistrationRequestApproveForm
    permission_required = ('players.view_any_player')

    def get_success_url(self):
        """
        The form has been successful.

        Now, we want to create the success url
        """
        return reverse('registration:request_list')

    def form_valid(self, form):
        """
        
        """
        # update the request status and add the order id
        registration_request = RegistrationRequest.objects.get(
            pk=self.kwargs.get('pk')
        )
        registration_request.status = COMPLETE
        registration_request.save()
        
        RegistrationRequest.request_complete(
            registration_request.id,
            registration_request.player.user,
            self.request
        )

        return super().form_valid(form)


class RegistrationRequestDenyFormView(
        PermissionRequiredMixin,
        FormView
        ):

    form_class = RegistrationRequestDenyForm
    permission_required = ('players.view_any_player')

    def get_success_url(self):
        """
        The form has been successful.

        Now, we want to create the success url
        """
        return reverse('registration:request_list')

    def form_valid(self, form):
        """
        
        """
        # update the request status and add the order id
        registration_request = RegistrationRequest.objects.get(
            pk=self.kwargs.get('pk')
        )
        registration_request.status = DENIED
        registration_request.save()

        messages.info(self.request, f"Request Denied for {registration_request.player}")
        return super().form_valid(form)


class RegistrationRequestPayAtDoorView(
        LoginRequiredMixin,
        UserPassesTestMixin,
        RedirectView
        ):
    """
    Someone is indicating that they will pay at the door.

    This should continue the sign up so that the player is registered.

    Updates the registration request to add the pay_at_door_flag

    Then moves the user on to completing the registration
    """
    pattern_name = 'registration:complete'

    def test_func(self):
        if self.request.user.has_perm('players.view_any_player'):
            return True
        try:
            player = RegistrationRequest.objects.get(pk=self.kwargs['pk']).player
            return (player.user == self.request.user)
        except RegistrationRequest.DoesNotExist:
            return False
        return False

    def get_redirect_url(self, *args, **kwargs):
        # get the registration request id
        registration_request = RegistrationRequest.objects.get(pk=self.kwargs['pk'])
        # and set the correct flag.
        registration_request.pay_at_door_flag = True
        registration_request.save(update_fields=['pay_at_door_flag'])
        RegistrationRequest.request_complete(
            self.kwargs['pk'],
            self.request.user,
            self.request
        )
        del kwargs['pk']
        return super().get_redirect_url(*args, **kwargs)


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
