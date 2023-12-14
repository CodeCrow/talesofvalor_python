"""
These are views that are used for viewing and editing Between game skills.

BGS are written by players and .
"""
from django.contrib.auth.mixins import LoginRequiredMixin, \
    PermissionRequiredMixin, UserPassesTestMixin
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, \
    DeleteView
from django.views.generic import DetailView, ListView

from talesofvalor.attendance.models import Attendance
from talesofvalor.characters.models import Character
from talesofvalor.events.models import Event
from talesofvalor.players.models import Player

from .forms import BetweenGameAbilityForm
from .models import BetweenGameAbility


class BetweenGameAbilityCreateView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    CreateView
):
    """
    Allows the Creation of an Between Game Ability Request
    """
    form_class = BetweenGameAbilityForm
    model = BetweenGameAbility

    def test_func(self):
        if self.request.user.has_perm('players.change_any_player'):
            return True
        event = Event.objects.get(pk=self.request.GET.get('event_id', None))
        character = Character.objects.get(
            pk=self.request.GET.get(
                'character_id',
                self.request.user.player.active_character
                )
            )
        return event.attended(character)

    def get_initial(self):
        # Get the initial dictionary from the superclass method
        initial = super().get_initial()
        # see if we are getting the character or event from the query string.
        try:
            event_id = self.request.GET.get('event_id', None)
            initial['event'] = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            initial['event'] = Event.previous_event()
        try:
            character_id = self.request.GET.get('character_id', None)
            character_id = character_id if character_id else 0
            initial['character'] = Character.objects.get(id=character_id)
        except Character.DoesNotExist:
            if not self.request.user.has_perm('players.change_any_player'):
                initial['character'] = self.request.user.player.active_character
            else:
                pass

        # etc...
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # pass the 'user' in kwargs
        return kwargs

    def form_valid(self, form):
        """
        Add the modified and created by
        """
        bga = form.save(commit=False)
        bga.modified_by = bga.created_by = self.request.user.player
        bga.save()
        return super().form_valid(form)

    def get_success_url(self):
        return "%s?event_id=%s&character_id=%s" % (reverse(
            'betweengameabilities:betweengameability_list',
        ), self.object.event.id, self.object.character.id) 


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
    UserPassesTestMixin,
    UpdateView
):
    """
    Edits a Between Game skill that has already been created
    """

    model = BetweenGameAbility
    form_class = BetweenGameAbilityForm

    def test_func(self):
        if self.request.user.has_perm('players.change_any_player'):
            return True
        try:
            bga = BetweenGameAbility.objects.get(pk=self.kwargs.get('pk'))
            return (
                (bga.character.player.user == self.request.user) and
                (bga.created_by == self.request.user.player)
            )
        except BetweenGameAbility.DoesNotExist:
            return False
        return False

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # pass the 'user' in kwargs
        return kwargs

    def form_valid(self, form):
        """
        Add the modified by
        """
        bga = form.save(commit=False)
        bga.modified_by = self.request.user.player
        bga.save()
        return super().form_valid(form)

    def get_success_url(self):
        return "%s?event_id=%s&character_id=%s" % (reverse(
            'betweengameabilities:betweengameability_list',
        ), self.object.event.id, self.object.character.id)


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


class BetweenGameAbilityListView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    ListView
):
    """
    Show a list of BetweenGameAbilities.

    Limit by event if the event id is sent.
    Limit by player if the player id is sent.
    If the player id is not sent, limit the list to the current user
    if they don't have the permission to "view_any_player"

    There should be a modal to add comments to each BGA
    """

    model = BetweenGameAbility
    paginate_by = 25
    ordering = ['-event__event_date', 'character']

    def test_func(self):
        if self.request.user.has_perm('players.change_any_player'):
            return True
        event = Event.objects.get(pk=self.request.GET.get('event_id', None))
        return event.attended_player(self.request.user.player)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        event = character = player = None
        context = super().get_context_data(**kwargs)
        # get the event
        event_id = self.request.GET.get('event_id', None)
        if event_id:
            event = Event.objects.get(pk=event_id)
        else:
            event = Event.previous_event()
        # now filter based on what they are allowed to see
        if self.request.user.has_perm('players.view_any_player'):
            # if the player id was sent, filter by that.
            if self.request.GET.get('player_id', None):
                player = Player.objects.get(pk=self.request.GET['player_id'])
        else:
            player = self.request.user.player
        if player:
            character = player.active_character
        context['event'] = event
        context['character'] = character
        return context

    def get_queryset(self):
        player = None
        queryset = super().get_queryset()
        # filter by event

        event_id = self.request.GET.get('event_id', None)
        if event_id:
            queryset = queryset.filter(event__id=event_id)
        else:
            event = Event.next_event()
            event_id = None if not event else event.id
        # now filter based on what they are allowed to see
        if self.request.user.has_perm('players.view_any_player'):
            # if the player id was sent, filter by that.
            if self.request.GET.get('player_id', None):
                player = Player.objects.get(pk=self.request.GET['player_id'])
        else:
            player = self.request.user.player
        if player:
            characters = player.character_set.all()
            queryset = queryset.filter(character__in=characters)
        return queryset


