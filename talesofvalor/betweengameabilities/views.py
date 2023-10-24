"""
These are views that are used for viewing and editing Between game skills.

BGS are written by players and .
"""
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, \
    PermissionRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, \
    DeleteView
from django.views.generic import DetailView, ListView

from talesofvalor.events.models import Event

from .models import BetweenGameAbility


class BetweenGameAbilityCreateView(LoginRequiredMixin, CreateView):
    """
    Allows the Creation of an Between Game Ability Request
    """
    model = BetweenGameAbility
    fields = ("character",
              "event",
              "skill",
              "count",
              "question",)

    success_url = reverse_lazy('betweengameabilities:betweengameability_list')


class BetweenGameAbilityCharacterEventView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UserPassesTestMixin,
    DetailView
):
    """
    Show the BGA detail page for a character event.
    """
    model = Event
    template_name = "betweengamesabilities/characterevent_detail.html"


class BetweenGameAbilityUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UserPassesTestMixin,
    UpdateView
):
    """
    Edits a Between Game skill that has already been created
    """

    model = BetweenGameAbility
    fields = "__all__"
    permission_required = ('player.can_update_any_player',)
    success_url = reverse_lazy('betweengameabilities:betweengameabilities_list')

    def test_func(self):
        if self.request.user.has_perm('players.change_any_player'):
            return True
        try:
            bgs = BetweenGameAbility.objects.get(self.kwargs['pid'])
            return (bgs.character.player == self.request.user)
        except BetweenGameAbility.DoesNotExist:
            return False
        return False


class BetweenGameAbilityDeleteView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UserPassesTestMixin,
    DeleteView
):
    """
    Removes a between game ability request permanantly.
    """

    model = BetweenGameAbility
    success_url = reverse_lazy('betweengameabilities:betweengameabilities_list')

    def test_func(self):
        if self.request.user.has_perm('players.change_any_player'):
            return True
        try:
            bgs = BetweenGameAbility.objects.get(self.kwargs['pid'])
            return (bgs.character.player == self.request.user)
        except BetweenGameAbility.DoesNotExist:
            return False
        return False


class BetweenGameAbilityDetailView(LoginRequiredMixin, DetailView):
    """
    Show the details for a between game ability request.
    """

    model = BetweenGameAbility
    fields = '__all__'


class BetweenGameAbilityListView(LoginRequiredMixin, ListView):
    """
    Show a list of BetweenGameAbilities.

    Limit by event if the event id is sent.
    Limit by player if the player username is sent.
    If the player username is not sent, limit the list to the current user
    if they don't have the permission to "view_any_player"

    There should be a modal to add comments to each BGA
    """

    model = BetweenGameAbility
    paginate_by = 25
    ordering = ['-event__event_date', 'character']

    def get_queryset(self):
        user = None
        queryset = super().get_queryset()
        # filter by event

        event_id = self.kwargs.get('event_id', None)
        if event_id:
            queryset = queryset.filter(event__id=event_id)
        # now filter based on what they are allowed to see
        if self.request.user.has_perm('players.view_any_player'):
            # if the username was sent, filter by that.
            if self.request.GET.get('username', None):
                user = User.objects.get(username=self.request.GET['username'])
        else:
            user = self.request.user
        if user:
            characters = user.player.character_set.all()
            queryset = queryset.filter(character__in=characters)
        return queryset
