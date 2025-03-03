"""
These are views that are used for viewing and editing Between game skills.

BGA are written by players and .
"""
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, \
    PermissionRequiredMixin, UserPassesTestMixin
from django.core import mail
from django.db.models import Q
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic.edit import CreateView, DeleteView, FormMixin,\
    UpdateView
from django.views.generic import DetailView, ListView


from talesofvalor import get_query
from talesofvalor.characters.models import Character
from talesofvalor.events.models import Event
from talesofvalor.players.models import Player

from .forms import BetweenGameAbilityForm, BetweenGameAbilityAnswerForm
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
        # set up current time
        now = timezone.localtime(timezone.now())
        event = Event.objects.get(pk=self.request.GET.get('event_id', 0))
        if now.date() > event.bgs_due_date:
            return False
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
            event_id = self.request.GET.get('event_id', 0)
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
            # set up current time
            now = timezone.localtime(timezone.now())
            if now.date() > bga.event.bgs_due_date:
                return False
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


class BetweenGameAbilityDetailView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    FormMixin,
    DetailView
):
    """
    Show the details for a between game ability request.
    """

    model = BetweenGameAbility
    form_class = BetweenGameAbilityAnswerForm

    def test_func(self):
        if self.request.user.has_perm('players.change_any_player'):
            return True
        try:
            bga = BetweenGameAbility.objects.get(pk=self.kwargs.get('pk'))
            return bga.character.player.user == self.request.user
        except BetweenGameAbility.DoesNotExist:
            return False
        return False

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)
        if self.request.POST:                
            context['form'] = self.form_class(
                instance=self.object,
                data=self.request.POST
            )
        else:
            context['form'] = self.form_class(instance=self.object)
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        form = context['form']
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        bga = form.save(commit=False)
        if len(form.cleaned_data.get('answer', '')) == 0:
            bga.answer_date = None
        else:
            bga.answer_date = timezone.now()
        bga.save()
        # save the tags
        form.save_m2m()
        result = super().form_valid(form)
        # send an email if the assigned_to field has changed 
        if 'assigned_to' in form.changed_data:
            assigned_to = form.cleaned_data.get('assigned_to')
            message = """
            Hello {}!

            You have had a Between Game Ability assigned to you.

            See it here:
            {}

            --ToV MechCrow
            """.format(
                    assigned_to.user.first_name,
                    self.request.build_absolute_uri(
                        reverse("betweengameabilities:betweengameability_detail", kwargs={
                            'pk': form.instance.id
                        })
                    )
                )
            email_message = mail.EmailMessage(
                "BGA assigned to you",
                message,
                settings.DEFAULT_FROM_EMAIL,
                (assigned_to.user.email, )
            )
            email_message.send()
        return result

    def get_success_url(self):
        return reverse(
            'betweengameabilities:betweengameability_detail',
            kwargs={'pk': self.object.pk}
        )


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
        if not self.event:
            return False
        return self.event.attended_player(self.request.user.player)

    def dispatch(self, request, *args, **kwargs):
        # get the event
        self.event = None
        event_id = self.request.GET.get('event_id', None)
        if event_id:
            try:
                self.event = Event.objects.get(pk=event_id)
            except Event.DoesNotExist:
                pass
        if not self.event:
            self.event = Event.previous_event()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        character = player = None
        context = super().get_context_data(**kwargs)

        # now filter based on what they are allowed to see
        if self.request.user.has_perm('players.view_any_player'):
            # if the player id was sent, filter by that.
            if self.request.GET.get('player_id', None):
                player = Player.objects.get(pk=self.request.GET['player_id'])
        else:
            player = self.request.user.player
        if player:
            character = player.active_character

        # get the list of events so we can pick from them to filter the lists.
        context['event_list'] = Event.objects.all()
        context['event'] = self.event
        context['character'] = character
        return context

    def get_queryset(self):
        player = None
        queryset = super().get_queryset()
        # do we only want to view items assigned to me?
        assigned = int(self.request.GET.get('assigned', 0))
        if assigned:
            queryset = queryset.filter(assigned_to=self.request.user.player)
        # show only bga without an answer
        unanswered = True if int(self.request.GET.get('unanswered', 0)) > 0 else False
        if unanswered:
            queryset = queryset.filter(
                Q(answer_date__isnull=True)
            )
            # more complicated query that deals with situaltions 
            # where people submit without entering information.
            '''
            queryset = queryset.filter(
                Q(answer_date__isnull=True) |
                Q(answer__isnull=True) |
                Q(answer__regex=r"\S+")
            )
            '''
        # filter by character/player name
        name = self.request.GET.get('name', '')
        if (name.strip()):
            entry_query = get_query(
                name,
                ['character__player__user__username', 'character__player__user__first_name', 'character__player__user__last_name', 'character__name']
            )
            queryset = queryset.filter(entry_query)
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


