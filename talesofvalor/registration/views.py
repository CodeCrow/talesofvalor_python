from django.conf import settings
from django.views.generic import TemplateView, DetailView
from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment

from talesofvalor.players.models import RegistrationRequest

# Creating Access Token for Sandbox
client_id = settings.PAYPAL_CLIENT_ID
client_secret = settings.PAYPAL_CLIENT_SECRET
# Creating an environment
environment = SandboxEnvironment(
    client_id=client_id,
    client_secret=client_secret
)
client = PayPalHttpClient(environment)


class RegistrationSendView(TemplateView):
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
        context_data['PAYPAL_CLIENT_ID'] = client_id
        context_data['PAYPAL_CLIENT_SECRET'] = client_secret
        return context_data

class RegistrationCompleteView(DetailView):
    template_name = "registration/registration_complete.html"
    model = RegistrationRequest
