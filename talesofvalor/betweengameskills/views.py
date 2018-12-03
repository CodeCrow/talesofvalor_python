"""
These are views that are used for viewing and editing Between game skills.

BGS are written by players and .
"""
from django.contrib.auth.mixins import LoginRequiredMixin,\
    PermissionRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView,\
    DeleteView, FormView
from django.views.generic import DetailView, ListView

from .models import BetweenGameSkill


class BetweenGameSkillCreateView(LoginRequiredMixin, CreateView):
    """
    Allows the Creation of an Between Game Skill
    """
    model = BetweenGameSkill
    fields = "__all__"
    success_url = reverse_lazy('betweengameskills:betweengameskill_list')


class BetweenGameSkillUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin, UpdateView):
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
        except DoesNotExist:
            return False
        return False

class BetweenGameSkillDeleteView(LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin, DeleteView):
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
        except DoesNotExist:
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
    Show the details for a character.

    From here you can edit the details of a character or choose skills.
    """

    model = BetweenGameSkill
    paginate_by = 25
