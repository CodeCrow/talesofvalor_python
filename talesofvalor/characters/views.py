"""These are views that are used for viewing and editing characters."""

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin,\
    LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import F
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic.edit import FormMixin, CreateView, UpdateView
from django.views.generic import DetailView, ListView, DeleteView

from rest_framework.status import HTTP_412_PRECONDITION_FAILED
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView

from talesofvalor.skills.models import Header, Skill, HeaderSkill

from .models import Character
from .forms import CharacterForm, CharacterSkillForm


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
            'characters:character_detail',
            kwargs={'pk': self.object.pk}
        )

    def form_valid(self, form):
        """
        If this form is valid, then add the current player to the character
        if the current user is not an admin
        """
        if not self.request.user.has_perm('players.view_any_player'):
            form.instance.player = self.request.user.player
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
        context['skills'] = filter(lambda x:  x.id in available_skills, self.skills)

        # if this is a user who can see all skills, just return the skill hash.
        '''
        if self.request.user.has_perm('players.view_all_skills'):
            context['skill_hash'] = Skill.skillhash()
        else:
            # otherwise, limit the displayed skills to those the character
            # should have.
            context['skill_hash'] = self.object.skillhash
        '''
        context['skill_hash'] = self.object.skillhash
        # add the bare skills granted by the rules
        context['granted_skills'] = self.object.skill_grants()  
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
        print("CHARACTER HEADERS:{}".format(character.headers.all()))
        # check that the header is allowed.
        print("HEADER CHECK:{}".format(character.check_header_prerequisites(header)))
        # Default to error.
        content = {
            'error': "prerequisites not met"
        }
        status = None
        print("HEADER COST:{}".format(header.cost))
        # if the prerequisites are met, add the header to the user and return
        # the list of skills
        if character.check_header_prerequisites(header):
            # see if the character has enough points to add the header
            if (cp_available - header.cost) > 0:
                print("HEADER:{}".format(header.__dict__))
                character.cp_available -= header.cost
                character.cp_spent += header.cost
                character.headers.add(header)
                print("CHARACTER:{}".format(character.__dict__))
                character.save()
                print("SKILLS:{}".format(header.skills.all()))
                skill_item_template_string = render_to_string(
                    "characters/includes/character_skill_item.html",
                    {
                        'header': header,
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
                    'error': "not enough points"
                }
                status = HTTP_412_PRECONDITION_FAILED
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
            cost = header_skill.cost * vector
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
                    'error': "not enough points"
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


class CharacterListView(LoginRequiredMixin, ListView):
    """
    Show the list of characters.

    From here, you can view, edit, delete a character.
    """

    model = Character
    paginate_by = 25
