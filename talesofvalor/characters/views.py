"""These are views that are used for viewing and editing characters."""

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin,\
    LoginRequiredMixin, PermissionRequiredMixin
from django.db import transaction
from django.db.models import F
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic.edit import FormMixin, CreateView, UpdateView
from django.views.generic import DeleteView, DetailView, FormView, ListView

from rest_framework.status import HTTP_412_PRECONDITION_FAILED
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView


from talesofvalor import get_query
from talesofvalor.events.models import Event
from talesofvalor.players.models import Registration
from talesofvalor.skills.models import Header, HeaderSkill

from .models import Character
from .forms import CharacterForm, CharacterSkillForm,\
    CharacterConceptApproveForm, CharacterHistoryApproveForm


class OwnsCharacter(BasePermission):
    """
    The current user is staff or owns the that is being manipulated.
    """
    message = "You don't own this character"

    def has_object_permission(self, request, view, obj):
        if self.request.user.has_perm('players.view_any_player'):
            return True
        try:
            player = Character.objects.get(pk=self.kwargs['pk']).player
            return (player.user == self.request.user)
        except Character.DoesNotExist:
            return False
        return False


class CharacterCreateView(LoginRequiredMixin, CreateView):
    model = Character
    form_class = CharacterForm

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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # pass the 'user' in kwargs
        return kwargs

    def get_success_url(self):
        return reverse(
            'characters:character_skill_update',
            kwargs={'pk': self.object.pk}
        )

    def form_valid(self, form):
        """
        If this form is valid, then add the current player to the character
        if the current user is not an admin

        If the user doesn't have any other active characters, set this one
        to active.
        """
        if not self.request.user.has_perm('players.view_any_player'):
            form.instance.player = self.request.user.player

        if not form.instance.player.character_set.filter(active_flag=True).exists():
            form.instance.active_flag = True

        messages.info(self.request, 'New Character, "{}" created.'.format(
            form.instance.name
        ))
        return super().form_valid(form)


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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # pass the 'user' in kwargs
        return kwargs

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
    permission_required = ('characters.change_character', )
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


class CharacterResetView(
        PermissionRequiredMixin,
        UserPassesTestMixin,
        View
        ):
    """
    Resets a characters skills to none and returns their points to them.
    """

    model = Character
    permission_required = ('characters.change_character', )
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

    def get(self, request, *args, **kwargs):
        """
        Send the user back to the the originating page or back to the
        character they are setting active
        """

        with transaction.atomic():
            character = self.model.objects.get(pk=self.kwargs['pk'])
            character.cp_available += character.cp_spent
            character.cp_spent = 0
            character.save(update_fields=['cp_available', 'cp_spent'])
            character.characterskills_set.all().delete()
            character.headers.clear()
        messages.info(self.request, 'Character skills reset for {}.'.format(
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
        kwargs = super().get_form_kwargs()
        self.skills = Header.objects\
            .order_by('hidden_flag', 'category', 'name')\
            .all()
        kwargs.update({'skills': self.skills})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**self.kwargs)

        # remove skills not in the hash.
        available_skills = self.object.skillhash.keys()
        context['skills'] = filter(lambda x:  x.id in available_skills or self.request.user.has_perm('player.view_any_player'), self.skills)
        context['skill_hash'] = self.object.skillhash
        # add the bare skills granted by the rules
        context['granted_skills'] = self.object.skill_grants
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
        return super().form_valid(form)


class ResetPointsView(
        PermissionRequiredMixin,
        View
        ):
    """
    Resets the points for the season.
    """

    permission_required = ('characters.reset_points', )

    def get(self, request, *args, **kwargs):
        """
        Send the user back to the the originating page or back to the main 
        page if the referrer isn't set.
        """
        Character.objects.all().update(cp_transferred=0)
        messages.info(self.request, 'Point cap reset!')
        return HttpResponseRedirect(
            self.request.META.get(
                'HTTP_REFERER',
                '/'
            )
        )


'''
Put the AJAX work for Characters here
'''


class CharacterAddHeaderView(APIView):
    '''
    Set of AJAX views for a Characters

    This handles different API calls for character actions.
    '''

    authentication_classes = [SessionAuthentication]
    permission_classes = [OwnsCharacter]

    def post(self, request, format=None):
        header_id = int(request.POST.get('header_id', 0))
        character_id = int(request.POST.get('character_id', 0))
        cp_available = int(request.POST.get('cp_available', 0))
        # get the character and then see if the header is allowed
        header = Header.objects.get(pk=header_id)
        character = Character.objects.get(pk=character_id)
        # Default to error.
        content = {
            'error': "prerequisites not met"
        }
        status = None
        # if the prerequisites are met, add the header to the user and return
        # the list of skills
        if character.check_header_prerequisites(header):
            # see if the character has enough points to add the header
            if (cp_available - header.cost) >= 0:
                character.cp_available -= header.cost
                character.cp_spent += header.cost
                character.headers.add(header)
                character.save()
                skill_item_template_string = render_to_string(
                    "characters/includes/character_skill_update_item.html",
                    {
                        'header': header,
                        'header_skills': header.skills.all(),
                        'header_costs': character.skillhash[header.id]
                    },
                    request
                )
                content = {
                    'success': header.cost * -1,
                    'skills': skill_item_template_string
                }
            else: 
                content = {
                    'error': "You don't have enough points available for this character to add this header."
                }
                status = HTTP_412_PRECONDITION_FAILED
        else:
            status = HTTP_412_PRECONDITION_FAILED
        return Response(content, status)


class CharacterDropHeaderView(APIView):
    '''
    Set of AJAX views for a Characters

    This handles different API calls for character actions.
    '''

    authentication_classes = [SessionAuthentication]
    permission_classes = [OwnsCharacter]

    def post(self, request, format=None):
        header_id = int(request.POST.get('header_id', 0))
        character_id = int(request.POST.get('character_id', 0))
        # get the character and header
        header = Header.objects.get(pk=header_id)
        character = Character.objects.get(pk=character_id)
        # Default to error.
        content = {
            'error': "Header is not already bought!"
        }
        status = None
        # if the character has the header, drop it and refund the CP
        content['header_list'] = []

        if header in character.headers.all():
            print(f'Header present!  Dropping and adding back in {header.cost} CP...')
            character.cp_available += header.cost
            character.cp_spent -= header.cost
            character.headers.remove(header)
            skill_item_template_string = render_to_string(
                "characters/includes/character_skill_update_item.html",
                {
                    'header': header,
                    'header_skills': header.skills.all(),
                    'header_costs': character.skillhash[header.id]
                },
                request
            )
            content = {
                'success': header.cost,
            }
        else:
            status = HTTP_412_PRECONDITION_FAILED
        return Response(content, status)


class CharacterAddSkillView(APIView):
    '''
    Set of AJAX views for a Characters

    This handles different API calls for character actions.
    '''

    authentication_classes = [SessionAuthentication]
    permission_classes = [OwnsCharacter]

    def post(self, request, format=None):
        skill_id = int(request.POST.get('skill_id', 0))
        header_id = int(request.POST.get('header_id', 0))
        character_id = int(request.POST.get('character_id', 0))
        cp_available = int(request.POST.get('cp_available', 0))
        try:
            vector = int(request.POST.get('vector'))
        except AttributeError:
            return {
                'error': "No change indicated"
            }
        # get the character and then see if the skill is allowed
        header_skill = HeaderSkill.objects.get(skill_id=skill_id, header_id=header_id)
        character = Character.objects.get(pk=character_id)
        # check that the skill is allowed.
        # if the prerequisites are met, add the header to the user and return
        # the list of skills
        # otherwise, return an error
        content = {
            'success': "testing right now"
        }
        status = None
        if character.check_skill_prerequisites(header_skill.skill, header_skill.header):
            # since vector is the direction, we want to reverse it when
            # dealing with what we want to change for the available points
            # see if the character has enough points to add the header
            cost = character.skill_cost(header_skill) * vector
            if (cp_available - cost) >= 0:
                # when this is returned, change the available costs
                (character_skill, created) = character.characterskills_set.get_or_create(
                    skill=header_skill
                )
                if character_skill.count and (character_skill.count + vector < 0):
                    content = {
                        'error': f"You don't have any points in {header_skill.skill}"
                    }
                    status = HTTP_412_PRECONDITION_FAILED
                else:                
                    content = {
                        'success': cost * -1
                    }
                    character_skill.count = F('count') + vector
                    character_skill.save()
                    character.cp_spent = F('cp_spent') + cost
                    character.cp_available = F('cp_available') - cost
                    character.save()
            else: 
                content = {
                    'error': "You don't have enough points available to purchase this skill . . ."
                }
                status = HTTP_412_PRECONDITION_FAILED
        return Response(content, status)


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


class CharacterConceptApproveView(PermissionRequiredMixin, FormView):
    """
    Approve the concept for a character.
    Grant the CP for the character
    Set the history approved flag.
    """
    permission_required = 'players.change_any_player'
    form_class = CharacterConceptApproveForm

    def form_valid(self, form):
        self.object = Character.objects.get(pk=form.cleaned_data['character_id'])
        self.object.player.cp_available += 3
        self.object.player.save(update_fields=['cp_available'])
        self.object.concept_approved_flag = True
        self.object.save(update_fields=['concept_approved_flag'])
        messages.info(self.request, f"{self.object} concept approved!")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object = Character.objects.get(pk=form.cleaned_data['character_id'])
        for key, error in form.errors.items():
            messages.error(self.request, error.as_text())
        return HttpResponseRedirect(reverse(
            'characters:character_detail',
            kwargs={'pk': self.object.pk}
        ))

    def get_success_url(self):
        return reverse(
            'characters:character_detail',
            kwargs={'pk': self.object.pk}
        )   


class CharacterHistoryApproveView(PermissionRequiredMixin, FormView):
    """
    Approve the history for a character.
    Grant the CP for the character
    Set the history approved flag.
    """
    permission_required = 'players.change_any_player'
    form_class = CharacterHistoryApproveForm

    def form_valid(self, form):
        self.object = Character.objects.get(pk=form.cleaned_data['character_id'])
        self.object.player.cp_available += 3
        self.object.player.save(update_fields=['cp_available'])
        self.object.history_approved_flag = True
        self.object.save(update_fields=['history_approved_flag'])
        messages.info(self.request, f"{self.object} history approved!")
        return super().form_valid(form)

    def form_invalid(self, form):
        self.object = Character.objects.get(pk=form.cleaned_data['character_id'])
        for key, error in form.errors.items():
            messages.error(self.request, error.as_text())
        return HttpResponseRedirect(reverse(
            'characters:character_detail',
            kwargs={'pk': self.object.pk}
        ))

    def get_success_url(self):
        return reverse(
            'characters:character_detail',
            kwargs={'pk': self.object.pk}
        ) 


class CharacterListView(LoginRequiredMixin, ListView):
    """
    Show the list of characters.

    From here, you can view, edit, delete a character.
    """

    model = Character
    paginate_by = 25

    def get_queryset(self):
        queryset = super().get_queryset()
        criteria = self.request.GET.get('criteria', '')
        if (criteria.strip()):
            entry_query = get_query(
                criteria,
                ['name', 'description', 'concept', 'history', 'player_notes']
            )
            queryset = queryset.filter(entry_query)
        history_approved_flag = self.request.GET.get('history_approved_flag', False)
        if history_approved_flag:
            queryset = queryset.filter(history_approved_flag=True)
        concept_approved_flag = self.request.GET.get('concept_approved_flag', False)
        if concept_approved_flag:
            queryset = queryset.filter(concept_approved_flag=True)
        return queryset

    def get_context_data(self, **kwargs):
        '''
        Add the form so we can filter the characters.
        '''
        # get the context data to add to.
        context_data = super().get_context_data(**kwargs)
        context_data.update(**self.request.GET)
        # return the resulting context
        return context_data


class CharacterPrintListView(LoginRequiredMixin, ListView):
    """
    Show a list of characters to print.

    """

    model = Character
    template_name = "characters/character_print_list.html"

    def get_queryset(self):
        queryset = super().get_queryset()  # filter by event
        event_id = self.kwargs.get('event_id', None)
        if not event_id:
            event_id = Event.next_event().id
        player_ids = Registration.objects.filter(event__id=event_id).values_list('player_id', flat=True)
        queryset = queryset.filter(player__id__in=player_ids, npc_flag=False, active_flag=True)
        
        return queryset
