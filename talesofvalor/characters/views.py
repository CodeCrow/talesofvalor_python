"""These are views that are used for viewing and editing characters."""
from django.contrib.auth.mixins import UserPassesTestMixin,\
    LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import DetailView, ListView, DeleteView

from talesofvalor.players.models import Player

from .models import Character
from .forms import CharacterForm


class CharacterCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Character
    form_class = CharacterForm

    def test_func(self):
        if self.request.user.has_perm('players.change_any_player'):
            return True
        try:
            player = Player.objects.get(
                pk=self.request.GET.get('player', None)
            )
            return (player.user == self.request.user)
        except Player.DoesNotExist:
            return False
        return False

    def get_initial(self):
        # Get the initial dictionary from the superclass method
        initial = super(CharacterCreateView, self).get_initial()
        # Copy the dictionary so we don't accidentally change a mutable dict
        initial = initial.copy()
        # default to getting the player from the query String.
        try:
            initial['player'] = self.request.GET['player']
        except KeyError:
            initial['player'] = self.request.user.player
        # etc...
        return initial

    def get_success_url(self):
        return reverse(
            'characters:character_detail',
            kwargs={'pk': self.object.pk}
        )


class CharacterUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Character
    fields = '__all__'

    def test_func(self):
        if self.request.user.has_perm('players.view_any_player'):
            return True
        try:
            player = Character.objects.get(pk=self.kwargs['pk']).player
            return (player.user == self.request.user)
        except Character.DoesNotExist:
            return False
        return False

    def get_success_url(self):
        return reverse(
            'characters:character_detail',
            kwargs={'pk': self.object.pk}
        )


class CharacterDeleteView(
        PermissionRequiredMixin,
        UserPassesTestMixin,
        DeleteView
        ):
    """
    Removes a character permanantly.

    Removing a character may have strange effects on other views.
    """

    model = Character
    permission_required = ('character.can_edit', )
    success_url = reverse_lazy('characters:character_list')

    def test_func(self):
        if self.request.user.has_perm('players.view_any_player'):
            return True
        try:
            player = Character.objects.get(pk=self.kwargs['pk']).player
            return (player.user == self.request.user)
        except Character.DoesNotExist:
            return False
        return False


class CharacterDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    Show the details for a character.

    From here you can edit the details of a character or choose skills.
    """

    model = Character
    fields = '__all__'

    def test_func(self):
        if self.request.user.has_perm('players.view_any_player'):
            return True
        try:
            player = Character.objects.get(pk=self.kwargs['pk']).player
            return (player.user == self.request.user)
        except Character.DoesNotExist:
            return False
        return False


class CharacterListView(LoginRequiredMixin, ListView):
    """
    Show the list of characters.

    From here, you can view, edit, delete a character.
    """

    model = Character
    paginate_by = 25
