"""These are views that are used for viewing and editing player app.

REFERENCE:

https://simpleisbetterthancomplex.com/tutorial/2017/02/18/how-to-create-user-sign-up-view.html
https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#abstractbaseuser
"""

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin,\
    LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login
from django.db.models import F
from django.http import HttpResponseRedirect
from django.views.generic import DetailView, ListView
from django.views.generic.base import RedirectView
from django.views.generic.edit import CreateView, UpdateView, DeleteView,\
    FormView, FormMixin, ProcessFormView
from django.urls import reverse, reverse_lazy

from rest_framework.response import Response
from rest_framework.views import APIView

from talesofvalor import get_query
from talesofvalor.events.models import Event
from talesofvalor.attendance.models import Attendance

from .forms import RegistrationForm,\
    MassRegistrationForm, MassAttendanceForm, MassEmailForm,\
    MassGrantCPForm, TransferCPForm
from .models import Player, Registration


class PlayerCreateView(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        CreateView
        ):
    '''
    Player is created.

    when the player is created, we have to make sure that they are added
    to the group "Player"
    '''

    model = Player
    fields = '__all__'
    permission_required = ('players.create_player', )


class PlayerUpdateView(
        LoginRequiredMixin,
        PermissionRequiredMixin,
        UserPassesTestMixin,
        UpdateView
        ):
    model = Player
    fields = '__all__'
    permission_required = ('players.change_player', )

    def test_func(self):
        if self.request.user.has_perm('players.change_any_player'):
            return True
        try:
            player = Player.objects.get(user__username=self.kwargs['username'])
            return (player.user == self.request.user)
        except Player.DoesNotExist:
            return False
        return False

    def get_object(self):
        return Player.objects.get(user__username=self.kwargs['username'])


class PlayerDeleteView(PermissionRequiredMixin, DeleteView):
    """
    Removes an player permanantly.

    This should have a confirmation, but it should never actually be deleted.
    It would have too many knock on effects (messages, etc)
    It should just become impossible to get to this player.
    """

    model = Player
    permission_required = ('player.can_edit', )
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

        player = self.request.user
        kwargs['username'] = player.username
        return super(PlayerRedirectDetailView, self).get_redirect_url(*args, **kwargs)


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
            player = Player.objects.get(user__username=self.kwargs['username'])
            return (player.user == self.request.user)
        except Player.DoesNotExist:
            return False
        return False

    def get_object(self):
        # or request.POST
        return Player.objects.get(user__username=self.kwargs['username'])

    def get_form_kwargs(self):
        kwargs = super(PlayerDetailView, self).get_form_kwargs()
        kwargs.update({
                'player': self.object
            })
        return kwargs

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
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
            kwargs={'username': self.object.user.username}
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
            kwargs={'username': self.instance.user.username}
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
                event=form.cleaned_data['event_attended']
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
                ['user__username', 'user__first_name', 'user__last_name', 'user__email']
            )
            queryset = queryset.filter(entry_query)
        selected = self.request.GET.get('selected', False)
        if selected:
            queryset = queryset.filter(id__in=self.request.session.get('player_select', []))
        registered_for = self.request.GET.get('registered_for', None)
        if registered_for:
            # get a list of players who are registered for the selected event.
            registered_players = Registration.objects.filter(event=registered_for).values_list('id', flat=True)
            queryset = queryset.filter(id__in=registered_players)
        attended = self.request.GET.get('attended', None)
        if attended:
            attended_players = Attendance.objects.filter(event=attended).values_list('id', flat=True)
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
        context = super(MassGrantCPView, self).get_context_data(**kwargs)
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