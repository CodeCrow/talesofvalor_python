"""These are views that are used for viewing and editing player app.

REFERENCE:

https://simpleisbetterthancomplex.com/tutorial/2017/02/18/how-to-create-user-sign-up-view.html
"""
from django.views.generic.edit import CreateView, UpdateView, FormView

from .forms import UserForm, PlayerForm, RegistrationForm
from .models import Player

class PlayerCreateView(CreateView):
    model = Player
    fields = '__all__'

class PlayerUpdateView(UpdateView):
    model = Player
    fields = '__all__'

    def get_object(self):
        return Player.objects.get(user__username=self.kwargs['username']) # or request.POST

class RegistrationView(FormView):
    template_name = 'players/registration_form.html'
    form_class = RegistrationForm

    def get_context_data(self, **kwargs):
        data = super(RegistrationView, self).get_context_data(**kwargs)

        if self.request.POST:
            data['user_form'] = UserForm(self.request.POST)
            data['player_form'] = PlayerForm(self.request.POST)
        else:
            data['user_form'] = UserForm()
            data['player_form'] = PlayerForm()
        return data

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        form.send_email()
        return super(RegistrationView, self).form_valid(form)

    def get_success_url(self):
        return reverse('player_detail', kwargs={'pk': self.object.username})