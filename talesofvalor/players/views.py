"""These are views that are used for viewing and editing player app.

REFERENCE:

https://simpleisbetterthancomplex.com/tutorial/2017/02/18/how-to-create-user-sign-up-view.html
https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#abstractbaseuser
"""
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin,\
    LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login
from django.core.exceptions import MultipleObjectsReturned
from django.db.models import F
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic import DetailView, ListView
from django.views.generic.base import RedirectView
from django.views.generic.edit import DeleteView, UpdateView,\
    FormView, FormMixin
from django.urls import reverse, reverse_lazy

from rest_framework.response import Response
from rest_framework.views import APIView

from talesofvalor import get_query
from talesofvalor.events.models import Event
from talesofvalor.attendance.models import Attendance

from .forms import UserForm, PlayerViewable_UserForm, PlayerForm,\
    PlayerViewable_PlayerForm, \
    RegistrationForm, MassRegistrationForm, MassAttendanceForm, MassEmailForm,\
    MassGrantCPForm, TransferCPForm, PELUpdateForm
from .models import Player, Registration, RegistrationRequest, PEL


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
                        player=self.object
                    )
                except RegistrationRequest.DoesNotExist:
                    event.registration_request = None 
                event.registration = None
        context['future_event_list'] = future_event_list
        # for each event, indicate if the user is registered for it or attended.
        past_event_list = Event.objects\
            .filter(event_date__lt=datetime.today())\
            .order_by('-event_date')
        for event in past_event_list:
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
        return super(PlayerDetailView, self).form_invalid(form)

    def form_valid(self, form):
        self.object.cp_available = self.object.cp_available - form.cleaned_data['amount']
        form.cleaned_data['character'].cp_transferred = form.cleaned_data['character'].cp_transferred + form.cleaned_data['amount']
        form.cleaned_data['character'].cp_available = form.cleaned_data['character'].cp_available + form.cleaned_data['amount']
        form.cleaned_data['character'].save()
        self.object.save()
        return super(PlayerDetailView, self).form_valid(form)

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
        groups = self.request.GET.get('group', None)
        if groups:
            queryset = queryset.filter(user__groups__name__in=[groups])
        name = self.request.GET.get('name', '')
        if (name.strip()):
            entry_query = get_query(
                name,
                ['player__user__username', 'player__user__first_name', 'player__user__last_name', 'player__user__email', 'player__player_pronouns']
            )
            queryset = queryset.filter(entry_query)
        selected = self.request.GET.get('selected', False)
        if selected:
            queryset = queryset.filter(id__in=self.request.session.get('player_select', []))

        for pel in queryset:
            print(f'\npel: player={pel.player}, pel.event={pel.event}, pel.event.id={pel.event.id}\n')

        attended = self.request.GET.get('attended', None)
        print(f'**************** attended {attended}')
        if attended:
            # attended_players = Attendance.objects.filter(event__id=attended).values_list('player__id', flat=True)
            attended_players = Attendance.objects.filter(event__id=attended)
            print('foo')
            print(f'attendance: {Attendance.objects.all()}\n')
            print('bar')
            queryset = queryset.filter(id__in=attended_players)

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


class PELDetailView(UserPassesTestMixin, DetailView):
    '''
    Show a particular PEL
    '''
    model = PEL
    permission_required = ('pels.view_pel', )
    show_staff_comments = True # self.request.user.has_perm('players.show_pel_staff_comments')
    edit_staff_comments = True # self.request.user.has_perm('players.edit_pel_staff_comments')

    def test_func(self):
        if self.request.user.has_perm('players.view_any_player'):
            return True
        try:
            pel = PEL.objects.get(player=self.object.player)
            return (pel.player.user == self.request.user)
        except PEL.DoesNotExist:
            return False
        return False

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
                'player_id': self.kwargs['player_id']
            }))


class PELRedirectView(RedirectView): 
    pattern_name = 'players:pel_detail'

    def get_redirect_url(self, *args, **kwargs):
        """
        Figure out where the user should be redirected to if they want to
        register for the next game.
        """
        try: 
            event = Event.objects.get(pk=self.kwargs['event_id'])
            player = Player.objects.get(user__username=self.kwargs['player_id'])
            kwargs['pk'] = PEL.objects.get(event=event, player=player).id
            del(kwargs['event_id'])
            del(kwargs['player_id'])
        except PEL.DoesNotExist:
            return reverse("players:pel_update", kwargs=kwargs)
        return super().get_redirect_url(*args, **kwargs)


class PELUpdateView(LoginRequiredMixin, UpdateView):
    form_class = PELUpdateForm

    return_url = None

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_object(self):
        '''
        get the object for this update, or create it.
        Object is retrieved based on the current user and the 
        sent event.  If it does not exist, it is created.
        '''
        event = Event.objects.get(pk=self.kwargs['event_id'])
        player = Player.objects.get(user__pk=self.kwargs['pk'])
        pel_object, created = PEL.objects.get_or_create(event=event, player=player)
        return pel_object

    def form_valid(self, form):
        '''
        send the user back where they came from
        Because they could have come from an event list
        or the PEL list
        '''
        self.return_url = form.cleaned_data['return_url']
        return super().form_valid(form)

    def get_success_url(self):
        if self.return_url:
            return self.return_url
        return super().get_success_url()

