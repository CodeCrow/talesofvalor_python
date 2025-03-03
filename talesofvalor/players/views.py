"""These are views that are used for viewing and editing player app.

REFERENCE:

https://simpleisbetterthancomplex.com/tutorial/2017/02/18/how-to-create-user-sign-up-view.html
https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#abstractbaseuser
"""
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.auth.mixins import UserPassesTestMixin,\
    LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.core.exceptions import MultipleObjectsReturned
from django.db.models import F
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import DetailView, ListView
from django.views.generic.base import RedirectView
from django.views.generic.edit import CreateView, DeleteView, UpdateView,\
    FormView, FormMixin

from rest_framework.response import Response
from rest_framework.views import APIView

from talesofvalor import get_query
from talesofvalor.attendance.models import Attendance
from talesofvalor.characters.models import Character
from talesofvalor.events.models import Event

from .forms import UserForm, PlayerViewable_UserForm, PlayerForm,\
    PlayerViewable_PlayerForm, \
    RegistrationForm, MassRegistrationForm, MassAttendanceForm, MassEmailForm,\
    MassGrantCPForm, TransferCPForm, PELUpdateForm,\
    TagUpdateForm
from .models import Player, Registration, RegistrationRequest, PEL, REQUESTED


class PlayerUpdateView(
        LoginRequiredMixin,
        UserPassesTestMixin,
        DetailView
        ):
    template_name = 'players/player_form.html'
    permission_required = ('players.change_player', )
    model = Player

    def test_func(self):
        if self.request.user.has_perm('players.change_any_player'):
            return True
        try:
            player = Player.objects.get(user__id=self.kwargs['pk'])
            return (player.user == self.request.user)
        except Player.DoesNotExist:
            return False
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            if self.request.user.has_perm('player.change_any_player'):
                context['user_form'] = UserForm(
                    instance=self.object.user,
                    data=self.request.POST
                )
                context['player_form'] = PlayerForm(
                    instance=self.object,
                    data=self.request.POST
                )
            else:
                context['player_form'] = PlayerViewable_PlayerForm(
                    instance=self.object,
                    data=self.request.POST
                )
                context['user_form'] = PlayerViewable_UserForm(
                    instance=self.object.user,
                    data=self.request.POST
                )
        else:
            # adjust fields for different users
            if self.request.user.has_perm('player.change_any_player'):
                context['player_form'] = PlayerForm(instance=self.object)
                context['user_form'] = UserForm(instance=self.object.user)
            else:
                context['player_form'] = PlayerViewable_PlayerForm(instance=self.object)
                context['user_form'] = PlayerViewable_UserForm(instance=self.object.user)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(**kwargs)
        if context['player_form'].is_valid() and context['user_form'].is_valid():
            context['player_form'].save()
            context['user_form'].save() 
            messages.info(self.request, '{} Updated.'.format(self.object.user.username))
            if self.request.user.player == self.object:
                return HttpResponseRedirect(reverse(
                    'players:player_detail',
                    kwargs={'pk': self.object.pk}
                ))
            else:
                return HttpResponseRedirect(reverse('players:player_list'))
        return self.render_to_response(context)


class PlayerDeleteView(PermissionRequiredMixin, DeleteView):
    """
    Removes an player permanantly.

    This should have a confirmation, but it should never actually be deleted.
    It would have too many knock on effects (messages, etc)
    It should just become impossible to get to this player.
    """

    model = Player
    permission_required = ('players.delete_player', )
    success_url = reverse_lazy('players:player_list')

    def delete(request, *args, **kwargs):
        """
        Do the actual deletion work.

        This actually just correctly sets the status of the player and
        the characters associated with the player.
        """
        print("Nah man, we ain't actually going to do that.  Too dangerous.")
        print(args)
        print(kwargs)
        return HttpResponseRedirect(reverse('players:player_list'))


class PlayerRedirectDetailView(LoginRequiredMixin, RedirectView):
    """
    Redirect to the detail page of the player who is logged in.

    We are using this so that when a user logs in or goes to a 'home' page,
    this will move them to the appropriate player detail page.
    """

    pattern_name = 'players:player_detail'

    def get_redirect_url(self, *args, **kwargs):
        """
        Figure out where the user should be redirected to.

        User the user object that is in the request, redirect the
        browser to the correct player detail.
        """
        kwargs['pk'] = self.request.user.player.pk
        return super().get_redirect_url(*args, **kwargs)


class PlayerDetailView(
        LoginRequiredMixin,
        UserPassesTestMixin,
        FormMixin,
        DetailView
        ):
    """
    Show the details for a player.

    This acts as the "home page" for a player that will show their characters,
    information about the player, and player actions.
    """

    model = Player
    fields = '__all__'
    form_class = TransferCPForm

    def test_func(self):
        if self.request.user.has_perm('players.view_any_player'):
            return True
        try:
            player = Player.objects.get(pk=self.kwargs['pk'])
            return (player.user == self.request.user)
        except Player.DoesNotExist:
            return False
        return False

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
                'player': self.object
            })
        return kwargs

    def get_context_data(self, **kwargs):
        """
        Add context: The event lists
        """

        context = super().get_context_data(**kwargs)
        future_event_list = Event.objects\
            .filter(event_date__gte=datetime.today())
        # for each event, indicate if the user is registered for it.
        for event in future_event_list:
            try:
                event.registration = Registration.objects.get(event=event, player=self.object)
                event.registration_request = None
            except MultipleObjectsReturned:
                event.registration = Registration.objects.filter(event=event, player=self.object).first()
                event.registration_request = None
            except Registration.DoesNotExist:
                # see if we have a request
                try:
                    event.registration_request = RegistrationRequest.objects.get(
                        event_registration_item__events=event,
                        player=self.object,
                        status=REQUESTED
                    )
                except RegistrationRequest.MultipleObjectsReturned:
                    # this is a result of old code bouble requesting things or Paypal taking too long.
                    # take the latest, and send an email to the admins about the problem.
                    event.registration_request = RegistrationRequest.objects.filter(
                        event_registration_item__events=event,
                        player=self.object,
                        status=REQUESTED
                    ).order_by('-requested').first()
                    message = """
                    Hello Administrators!

                    Multiple Registration Requests for user {}

                    Click here to figure out which one is valid:
                    {}

                    --ToV MechCrow
                    """.format(
                            self.object,
                            self.request.build_absolute_uri(
                                reverse("players:player_detail", kwargs={
                                    'pk': self.object.id
                                })
                            ),
                            (f"{reverse('registration:request_list')}?"),
                        )
                    email_message = mail.EmailMessage(
                        "Multiple Registration Requests",
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        ("rob@crowbringsdaylight.com", "wyldharrt@gmail.com", "ambisinister@gmail.com" )
                    )
                    email_message.send()
                except RegistrationRequest.DoesNotExist:
                    event.registration_request = None 

                event.registration = None
        context['future_event_list'] = future_event_list
        # for each event, indicate if the user is registered for it or attended.
        past_event_list = Event.objects\
            .filter(event_date__lt=datetime.today())\
            .order_by('-event_date')
        for event in past_event_list:
            event.attendance = event.attendance_set.filter(player=self.object).first()
            event.registration = Registration.objects\
                .filter(event=event, player=self.object)\
                .order_by('-id')\
                .first()
            event.registration_request = None
            if not event.registration:
                # see if we have a request
                event.registration_request = RegistrationRequest.objects.filter(
                    event_registration_item__events=event,
                    player=self.object
                )\
                    .order_by('-requested')\
                    .first()
            event.attended = event.attended_player(self.object)
        context['past_event_list'] = past_event_list
        # Set up the log display for the player
        context['player_log'] = LogEntry.objects.filter(
            content_type=ContentType.objects.get_for_model(self.model),
            object_id=self.object.id
        )
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        for error in form.errors:
            messages.error(self.request, form.errors[error])
        messages.warning(self.request, 'Error transferring points.')
        return super().form_invalid(form)

    def form_valid(self, form):
        self.object.cp_available = self.object.cp_available - form.cleaned_data['amount']
        form.cleaned_data['character'].cp_transferred = form.cleaned_data['character'].cp_transferred + form.cleaned_data['amount']
        form.cleaned_data['character'].cp_available = form.cleaned_data['character'].cp_available + form.cleaned_data['amount']
        form.cleaned_data['character'].save()
        self.object.save()
        log_message = f"\"{form.cleaned_data['amount']}\" CP transferred from \"{self.object}\" to \"{form.cleaned_data['character']}\"."
        LogEntry.objects.create(
            user=self.request.user,
            content_type=ContentType.objects.get_for_model(self.model),
            object_id=self.object.id,
            object_repr=self.object.__str__(),
            action_flag=CHANGE,
            change_message=log_message
        )
        LogEntry.objects.create(
            user=self.request.user,
            content_type=ContentType.objects.get_for_model(Character),
            object_id=form.cleaned_data['character'].id,
            object_repr=form.cleaned_data['character'].__str__(),
            action_flag=CHANGE,
            change_message=log_message
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'players:player_detail',
            kwargs={'pk': self.object.pk}
        )


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
        # The player is automatically created using post_save signals
        # on the "Player" model
        self.instance = user.player
        # This is where other custom player fields (not included in a django User)
        # gets updated.
        self.instance.player_pronouns = form.cleaned_data['player_pronouns']
        self.instance.food_allergies = form.cleaned_data['food_allergies']
        # Don't forget to save!
        self.instance.save()
        user = authenticate(
            username=user.username,
            password=form.cleaned_data['password']
        )
        login(self.request, user)
        # return result
        return super(RegistrationView, self).form_valid(form)

    def get_success_url(self):
        return reverse(
            'players:player_detail',
            kwargs={'pk': self.instance.user.player.pk}
        )


class PlayerListRegistrationView(LoginRequiredMixin, FormView):
    """
    Deals with registering players.

    It only displays something if there is an error.

    Otherwise, it just goes back to the playerlist view and shows a message.
    """
    form_class = MassRegistrationForm
    success_url = reverse_lazy('players:player_list')
    template_name = 'players/registration_mass_form.html'

    def form_valid(self, form):
        """
        When the mass registration form is good, register the players.

        We could use bulk_create, except we want to call the 'save'
        for the model so the cabin and meal plan is updated.
        """
        players_selected = Player.objects.filter(
            id__in=self.request.session.get('player_select', [])
        )
        for player in players_selected:
            registration = Registration.objects.create(
                player=player,
                event=form.cleaned_data['event_registered']
            )
        messages.info(self.request, 'Players Registered.')
        # return result
        return super(PlayerListRegistrationView, self).form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, 'Invalid registrations.')
        return super(PlayerListRegistrationView, self).form_invalid(form)


class PlayerListAttendanceView(LoginRequiredMixin, FormView):
    """
    Deals with registering players.

    It only displays something if there is an error.

    Otherwise, it just goes back to the playerlist view and shows a message.
    """
    form_class = MassAttendanceForm
    success_url = reverse_lazy('players:player_list')
    template_name = 'players/attendance_mass_form.html'

    def form_valid(self, form):
        """
        When the mass registration form is good, register the players.

        We could use bulk_create, except we want to call the 'save'
        for the model so the cabin and meal plan is updated.
        """
        players_selected = Player.objects.filter(
            id__in=self.request.session.get('player_select', [])
        )
        for player in players_selected:
            attendance = Attendance.objects.create(
                player=player,
                event=form.cleaned_data['event_attended'],
                character=player.active_character
            )
        messages.info(self.request, 'Players Marked Attended.')
        # return result
        return super(PlayerListAttendanceView, self).form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, 'Invalid registrations.')
        return super(PlayerListAttendanceView, self).form_invalid(form)


class PlayerListView(LoginRequiredMixin, ListView):
    """
    Lists the players.

    A list of the players.  In the view, admin/staff will be able to edit/view
    any of the players.
    There will also be ways of filtering players and taking bulk actions.
    """

    model = Player
    paginate_by = 100

    def get_queryset(self):
        queryset = super(PlayerListView, self).get_queryset()
        groups = self.request.GET.get('group', None)
        if groups:
            queryset = queryset.filter(user__groups__name__in=[groups])
        name = self.request.GET.get('name', '')
        if (name.strip()):
            entry_query = get_query(
                name,
                ['user__username', 'user__first_name', 'user__last_name', 'user__email', 'food_allergies']
            )
            queryset = queryset.filter(entry_query)
        selected = self.request.GET.get('selected', False)
        if selected:
            queryset = queryset.filter(id__in=self.request.session.get('player_select', []))
        registered_for = self.request.GET.get('registered_for', None)
        if registered_for:
            # get a list of players who are registered for the selected event.
            registered_players = Registration.objects.filter(event=registered_for).values_list('player__id', flat=True)
            queryset = queryset.filter(id__in=registered_players)
        attended = self.request.GET.get('attended', None)
        if attended:
            attended_players = Attendance.objects.filter(event=attended).values_list('player__id', flat=True)
            queryset = queryset.filter(id__in=attended_players)
        select = self.request.GET.get('select', None)
        if select:
            if select == 'none':
                # remove all selected in the session.
                self.request.session['player_select'] = []
            elif select == 'filtered':
                # take the queryset and make all of them part of the 
                # session selection.
                PlayerViewSet.add_to_session_selection(self.request, queryset.values_list('id', flat=True))
        return queryset

    def get_context_data(self, **kwargs):
        '''
        Put data into the view.

        We want to create list of events to pick selections from.
        '''
        # get the context data to add to.
        context_data = super(PlayerListView, self).get_context_data(**kwargs)
        context_data.update(**self.request.GET)
        # get the list of events so we can pick from them to filter the lists.
        context_data['event_list'] = Event.objects.all()
        # set up the forms that appear in the list
        context_data['registration_form'] = MassRegistrationForm()
        context_data['attendance_form'] = MassAttendanceForm()
        # return the resulting context
        return context_data


'''
Put the AJAX work for Players here
'''


class PlayerViewSet(APIView):
    '''
    Set of AJAX views for a Player

    This handles different API calls for player actions.
    '''
    @staticmethod
    def add_to_session_selection(request, ids):
        # get the existing player selection:
        player_selection = request.session.get('player_select', [])
        for new_id in ids:
            if new_id > 0:
                if new_id not in player_selection:
                    player_selection.append(new_id)
            else:
                player_selection = [x for x in player_selection if x != abs(new_id)]
            request.session['player_select'] = player_selection
        return player_selection

    def post(self, request, format=None):
        ids = []
        new_id = int(request.POST.get('id', None))
        if new_id:
            ids.append(new_id)
        content = {
            'player_select': self.add_to_session_selection(request, ids)
        }

        return Response(content)


class MassEmailView(FormView):
    '''
    Form for mass emails.

    Allow a mass email to be sent from  the player list based on the
    list of selection of players.
    '''
    template_name = 'players/mass_email.html'
    form_class = MassEmailForm
    success_url = reverse_lazy('players:player_list')

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        # get the selcted players
        selected_players = self.request.session.get('player_select', None)
        if selected_players:
            form.send_email(Player.objects.filter(id__in=selected_players))
            messages.info(self.request, 'Emails sent!')

        else:
            # we should raise an error here so users know there is a problem.
            messages.warning(self.request, 'No players selected for email.')
        return super(MassEmailView, self).form_valid(form)


class MassGrantCPView(FormView):
    '''
    View for mass granting of CP.

    So that a bunch of the selcted players (held in the session
    variable) get a set amount of CP.
    '''
    template_name = 'players/mass_grantcp.html'
    form_class = MassGrantCPForm
    success_url = reverse_lazy('players:player_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['player_select'] = Player.objects.filter(
            id__in=self.request.session.get('player_select', [])
        )
        return context

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        # get the selcted players
        selected_players = self.request.session.get('player_select', [])
        if selected_players:
            Player.objects\
                .filter(id__in=selected_players)\
                .update(cp_available=F('cp_available') + form.cleaned_data['amount'])
            messages.info(self.request, 'Bulk CP updated!')
            log_entries = []
            player_content_type = ContentType.objects.get_for_model(Player)
            for player_id in selected_players:
                player = Player.objects.get(pk=player_id)
                log_entry = LogEntry(
                    user=self.request.user,
                    content_type=player_content_type,
                    object_id=player_id,
                    object_repr=player.__str__(),
                    action_flag=CHANGE,
                    change_message=f"{form.cleaned_data['amount']} added to {player} because {form.cleaned_data['reason']}."
                )
                log_entries.append(log_entry)
            LogEntry.objects.bulk_create(log_entries)

        else:
            # we should raise an error here so users know there is a problem.
            messages.warning(self.request, 'No players selected for grant.')
        return super(MassGrantCPView, self).form_valid(form)


class PELListView(PermissionRequiredMixin, ListView):
    '''
    List the PELs for staff memebers
    '''
    permission_required = ('players.view_any_player', )
    model = PEL
    paginate_by = 25  # if pagination is desired

    def get_queryset(self):
        queryset = super(PELListView, self).get_queryset()
        name = self.request.GET.get('name', '')
        if (name.strip()):
            entry_query = get_query(
                name,
                [
                    'character__name',
                    'character__player__user__username',
                    'character__player__user__first_name',
                    'character__player__user__last_name', 
                    'character__player__user__email', 
                ]
            )
            queryset = queryset.filter(entry_query)

        attended = self.request.GET.get('attended', None)
        if attended:
            queryset = queryset.filter(event__id=attended)

        return queryset

    def get_context_data(self, **kwargs):
        '''
        Put data into the view.

        We want to create list of events to pick selections from.
        '''
        # get the context data to add to.
        context_data = super(PELListView, self).get_context_data(**kwargs)
        context_data.update(**self.request.GET)
        # get the list of events so we can pick from them to filter the lists.
        context_data['event_list'] = Event.objects.all()
        # set up the forms that appear in the list
        context_data['registration_form'] = MassRegistrationForm()
        context_data['attendance_form'] = MassAttendanceForm()
        # return the resulting context
        return context_data


class PELDetailView(
        LoginRequiredMixin,
        UserPassesTestMixin,
        FormMixin,
        DetailView
        ):
    '''
    Show a particular PEL
    '''
    model = PEL
    form_class = TagUpdateForm
    permission_required = ('pels.view_pel', )

    def test_func(self):
        if self.request.user.has_perm('players.view_any_player'):
            return True
        try:
            pel = PEL.objects.get(pk=self.kwargs.get('pk'))
            return (pel.player.user == self.request.user)
        except PEL.DoesNotExist:
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

    def get(self, request, *args, **kwargs):
        '''
        Try to go to view the PEL.  If it doesn't exist yet, 
        present the form through the Generic editing view.
        '''
        try:
            return super().get(request, *args, **kwargs)
        except Http404:
            return redirect(reverse('players:pel_update', kwargs={
                'event_id': self.kwargs['event_id'],
                'character_id': self.kwargs['character_id']
            }))

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        form = context['form']
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'players:pel_detail',
            kwargs={'pk': self.object.id}
        )


class PELRedirectView(RedirectView): 

    def get_redirect_url(self, *args, **kwargs):
        """
        Figure out where the user should be redirected to if they want to do a
        PEL for the current game.
        """
        try: 
            event = Event.objects.get(pk=self.kwargs['event_id'])
            character = Character.objects.get(pk=self.kwargs['character_id'])
            try:
                kwargs['pk'] = PEL.objects.get(event=event, character=character).id
            except PEL.MultipleObjectsReturned:
                kwargs['pk'] = PEL.objects.filter(event=event, character=character).last().id
                PEL.objects.filter(
                    event=event,
                    character=character
                ).exclude(
                    id=kwargs['pk']
                ).delete()
            del(kwargs['event_id'])
            del(kwargs['character_id'])
            return reverse("players:pel_update", kwargs=kwargs)
        except PEL.DoesNotExist:
            return reverse("players:pel_create", kwargs=kwargs)
        return super().get_redirect_url(*args, **kwargs)


class PELCreateView(
        LoginRequiredMixin,
        UserPassesTestMixin,
        CreateView
        ):
    model = PEL
    form_class = PELUpdateForm
    return_url = None

    def test_func(self):
        if self.request.user.has_perm('players.view_any_player'):
            return True
        try:
            event = Event.objects.get(pk=self.kwargs['event_id'])
            character = Character.objects.get(pk=self.kwargs['character_id'])
            return Attendance.objects.filter(character=character, event=event).exists()
        except Event.DoesNotExist:
            return False
        return False

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_initial(self):
        # Get the initial dictionary from the superclass method
        initial = super().get_initial()
        initial['event'] = Event.objects.get(pk=self.kwargs['event_id'])
        initial['character'] = Character.objects.get(pk=self.kwargs['character_id'])

        return initial

    def form_valid(self, form):
        '''
        send the user back where they came from
        Because they could have come from an event list
        or the PEL list.

        Send an email to the staff.
        Add the CP if the player has submitted it in time.
        '''
        # set up current date
        now = timezone.localtime(timezone.now())
        self.return_url = form.cleaned_data['return_url']
        result = super().form_valid(form)
        # if the user has submitted in time, add point to the player.
        if now.date() <= form.cleaned_data.get('event').pel_due_date:
            form.instance.character.player.cp_available = F('cp_available') + PEL.ON_TIME_BONUS
            form.instance.character.player.save(update_fields=['cp_available'])
            LogEntry.objects.create(
                user=self.request.user,
                content_type=ContentType.objects.get_for_model(Player),
                object_id=form.instance.character.player.id,
                object_repr=form.instance.character.player.__str__(),
                action_flag=CHANGE,
                change_message=f"\"{form.instance.character.player}\" granted {PEL.ON_TIME_BONUS} CP for submitting PEL before the deadline {form.cleaned_data.get('event').pel_due_date.strftime('%A %m-%d-%Y, %H:%M:%S')}"
            )
        # Alert the staff
        message = """
        Hello Staff!

        Player {} has submitted a PEL.

        See it here:
        {}

        --ToV MechCrow
        """.format(
                form.instance.character.player,
                self.request.build_absolute_uri(
                    reverse("players:pel_detail", kwargs={
                        'pk': form.instance.id
                    })
                )
            )
        email_message = mail.EmailMessage(
            f"PEL submitted by {form.cleaned_data.get('character').player}",
            message,
            settings.DEFAULT_FROM_EMAIL,
            (settings.STAFF_EMAIL, )
        )
        email_message.send()
        return result

    def get_success_url(self):
        if self.return_url:
            return self.return_url
        return reverse("players:player_redirect_detail")


class PELUpdateView(
        LoginRequiredMixin,
        UserPassesTestMixin,
        UpdateView
        ):
    model = PEL
    form_class = PELUpdateForm
    return_url = None

    def test_func(self):
        if self.request.user.has_perm('players.view_any_player'):
            return True
        try:
            pel = PEL.objects.get(pk=self.kwargs['pk'])
            player = pel.character.player
            return (player.user == self.request.user)
        except Event.DoesNotExist:
            return False
        return True

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        self.return_url = form.cleaned_data['return_url']
        result = super().form_valid(form)
        return result

    def get_success_url(self):
        if self.return_url:
            return self.return_url
        return reverse("players:player_redirect_detail")
