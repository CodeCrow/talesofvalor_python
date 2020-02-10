from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView
from django.views.generic.detail import DetailView
from paypalcheckoutsdk.orders import OrdersGetRequest

from talesofvalor.mixins import PayPalClientMixin
from talesofvalor.players.models import RegistrationRequest

from .forms import RegistrationCompleteForm


class RegistrationSendView(PayPalClientMixin, TemplateView):
    template_name = "registration/registration_send.html"

    def get_context_data(self, **kwargs):
        """
        This template should show the current pending request for the current
        user.

        It should show the current request (or indicate that there isn't one)
        and the paypal button.

        If there is no request, the paypal button should not be shown.
        """
        context_data = super().get_context_data(**kwargs)
        context_data['registration_requests'] = RegistrationRequest.objects.filter(player=self.request.user.player)
        context_data['PAYPAL_CLIENT_ID'] = self.client_id
        context_data['PAYPAL_CLIENT_SECRET'] = self.client_secret
        return context_data


class RegistrationCompleteView(PayPalClientMixin, FormView):
    template_name = "registration/registration_complete.html"
    form_class = RegistrationCompleteForm

    def get_success_url(self):
        """
        The form has been successful.

        Now, we want to create the success url, using the origin that was
        editted.
        """
        print(self.__dict__)
        return reverse_lazy('registration:detail', kwargs={
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

        return super().form_valid(form)


class RegistrationDetailView(DetailView):
    template_name = "registration/registrationrequest_detail.html"
    model = RegistrationRequest
