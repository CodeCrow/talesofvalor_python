"""
These are views that are used for viewing and editing Between game skills.

BGS are written by players and .
"""
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin,\
    PermissionRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView,\
    DeleteView
from django.views.generic import DetailView, ListView

from talesofvalor.events.models import Event

from .models import BetweenGameSkill


class BetweenGameSkillCreateView(LoginRequiredMixin, CreateView):
    """
    Allows the Creation of an Between Game Skill
    """
    model = BetweenGameSkill
    fields = "__all__"
    success_url = reverse_lazy('betweengameskills:betweengameskill_list')


class BetweenGameSkillCharacterEventView(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        UserPassesTestMixin,
        DetailView
        ):
    """
    Show the BGS detail page for a character event.
    """
    model = Event
    template_name = "betweengameskill/characterevent_detail.html"


class BetweenGameSkillUpdateView(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        UserPassesTestMixin,
        UpdateView
        ):
    """
    Edits a Between Game skill that has already been created
    """

    model = BetweenGameSkill
    fields = "__all__"
    success_url = reverse_lazy('betweengameskills:betweengameskills_list')

    def test_func(self):
        if self.request.user.has_perm('players.change_any_player'):
            return True
        try:
            bgs = BetweenGameSkill.objects.get(self.kwargs['pid'])
            return (bgs.character.player == self.request.user)
        except BetweenGameSkill.DoesNotExist:
            return False
        return False


class BetweenGameSkillDeleteView(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        UserPassesTestMixin,
        DeleteView
        ):
    """
    Removes a between game skill permanantly.
    """

    model = BetweenGameSkill
    success_url = reverse_lazy('betweengameskills:betweengameskills_list')

    def test_func(self):
        if self.request.user.has_perm('players.change_any_player'):
            return True
        try:
            bgs = BetweenGameSkill.objects.get(self.kwargs['pid'])
            return (bgs.character.player == self.request.user)
        except BetweenGameSkill.DoesNotExist:
            return False
        return False


class BetweenGameSkillDetailView(LoginRequiredMixin, DetailView):
    """
    Show the details for a character.

    From here you can edit the details of a character or choose skills.
    """

    model = BetweenGameSkill
    fields = '__all__'


class BetweenGameSkillListView(LoginRequiredMixin, ListView):
    """
    Show a list of BetweenGameSkills.

    Limit by event if the event id is sent.
    Limit by player if the player username is sent.
    If the player username is not sent, limit the list to the current user
    if they don't have the permission to "view_any_player"

    There should be a modal to add comments to each BGS
    """

    model = BetweenGameSkill
    paginate_by = 25
    ordering = ['-event__event_date', 'character']

    def get_queryset(self):
        user = None
        queryset = super().get_queryset()
        # filter by event
        if self.request.GET.get('event', None):
            queryset = queryset.filter(event=self.request.GET['event'])
        # now filter based on what they are allowed to see
        if self.request.user.has_perm('player.view_any_player'):
            # if the username was sent, filter by that.
            if self.request.GET.get('username', None):
                user = User.objects.get(username=self.request.GET['username'])
        else:
            user = self.request.user
        if user:
            characters = user.player.character_set()
            queryset = queryset.filter(character__in=characters)
        return queryset
