"""These are views that are used for viewing and editing player app.

REFERENCE:

https://simpleisbetterthancomplex.com/tutorial/2017/02/18/how-to-create-user-sign-up-view.html
https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#abstractbaseuser
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
    # We are making this too hard by tryig to link the 2 forms.
    # Just make one registration form (even if it has duplicates of the model fields!)
    # It will be easier and it will GET IT DONE.
    template_name = 'players/registration_form.html'
    form_class = RegistrationForm

    def form_invalid(self, form):
        print "I'm fucked!"
        print form.errors
        return super(RegistrationView, self).form_invalid(form)

    def form_valid(self, form):
        print "is the form valid?"
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.

        # return result
        return super(RegistrationView, self).form_valid(form)

    def get_success_url(self):
        return reverse('player_detail', kwargs={'pk': self.object.username})