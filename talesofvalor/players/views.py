"""These are views that are used for viewing and editing player app.

REFERENCE:

https://simpleisbetterthancomplex.com/tutorial/2017/02/18/how-to-create-user-sign-up-view.html
https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#abstractbaseuser
"""

from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.urls import reverse

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

class PlayerDetailView(DetailView):
    model = Player
    fields = '__all__'

    def get_object(self):
        return Player.objects.get(user__username=self.kwargs['username']) # or request.POST


class RegistrationView(FormView):
    """
    View where players first register.

    This is where the players will first sign up for the game.
    Originally, this was going to use the ModelView, but combining
    the user and player forms ended up being too hard.

    When the player is first registered, they are added to the
    'Player' group.
    """

    template_name = 'players/registration_form.html'
    form_class = RegistrationForm

    def form_invalid(self, form):
        """
        The form is invalid.

        There was an error.  Return the form and show errors.
        """
        print form.errors
        return super(RegistrationView, self).form_invalid(form)

    def form_valid(self, form):
        """
        If all valid information has been entered make a new player.

        All fields are valid.
        Now, make a new User.
        Tie that user to a new player.
        Add that player to the 'player' group.
        Drop the user into their detail.

        The player will not get an 'event started' until they register
        for their first event.
        """
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        user = User.objects.create_user(
            form.cleaned_data['username'],
            form.cleaned_data['email'],
            form.cleaned_data['password'],
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name']
        )
        # Find the player group and then add this user to it.
        try:
            player_group = Group.objects.get(name="Player")
        except Group.DoesNotExist:
            pass
        else:
            user.groups.add(player_group)
        # The player is automatically created using post_save signals on the "Player" model
        self.instance = user.player
        user = authenticate(username=user.username, password=form.cleaned_data['password'])
        login(self.request, user)
        # return result
        return super(RegistrationView, self).form_valid(form)

    def get_success_url(self):
        return reverse('players:player_detail', kwargs={'username': self.instance.user.username})
