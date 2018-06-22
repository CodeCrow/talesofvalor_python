"""These are views that are used for viewing and editing characters."""
from django.contrib.auth.mixins import UserPassesTestMixin,\
    LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.edit import CreateView, UpdateView

from .models import Character
from .forms import CharacterForm

class CharacterCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Character
    form_class = CharacterForm

    def test_func(self):
        if self.request.user.has_perm('players.change_any_player'):
            return True
        try:
            player = Player.objects.get(pk=self.kwargs['player'])
            return (player.user == self.request.user)
        except DoesNotExist:
            return False
        return False

    def get_initial(self):
        # Get the initial dictionary from the superclass method
        initial = super(CharacterCreateView, self).get_initial()
        # Copy the dictionary so we don't accidentally change a mutable dict
        initial = initial.copy()
        initial['player'] = self.request.GET['player']
           # etc...
        return initial

class CharacterUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Character
    fields = '__all__'