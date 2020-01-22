"""These are views that are used for viewing and editing characters."""

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin,\
    LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic.edit import FormMixin, CreateView, UpdateView
from django.views.generic import DetailView, ListView, DeleteView

from talesofvalor.players.models import Player
from talesofvalor.skills.models import Header

from .models import Character
from .forms import CharacterForm, CharacterSkillForm


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
    form_class = CharacterForm

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


class CharacterSetActiveView(
        LoginRequiredMixin,
        UserPassesTestMixin,
        View
        ):
    """
    Set the active character for the characters player to the sent id.
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

    def get(self, request, *args, **kwargs):
        """
        Send the user back to the the originating page or back to the
        character they are setting active
        """

        character = self.model.objects.get(pk=self.kwargs['pk'])
        character.player.character_set.update(active_flag=False)
        character.active_flag = True
        character.save()
        messages.info(self.request, 'Active Character changed to {}.'.format(
            character.name
        ))
        return HttpResponseRedirect(
            self.request.META.get(
                'HTTP_REFERER',
                reverse(
                    'characters:character_detail',
                    kwargs={'pk': self.kwargs['pk']}
                )
            )
        )


class CharacterSkillUpdateView(
        LoginRequiredMixin,
        UserPassesTestMixin,
        FormMixin,
        DetailView):
    """
    Allow a user to update their chosen skills
    """

    template_name = 'characters/character_skill_form.html'
    form_class = CharacterSkillForm
    model = Character

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

    def get_form_kwargs(self):
        kwargs = super(CharacterSkillUpdateView, self).get_form_kwargs()
        self.skills = Header.objects\
            .order_by('hidden', 'category', 'name')\
            .all()
        kwargs.update({'skills': self.skills})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(CharacterSkillUpdateView, self)\
            .get_context_data(**self.kwargs)
        context['skills'] = self.skills
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        """
        Form is valid.   Save the skills to that character and remove the
        appropriate number of characters points.
        """
        return super(CharacterSkillUpdateView, self).form_valid(form)


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
