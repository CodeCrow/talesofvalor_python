"""
These are views that are used for viewing and editing headers and skills.
"""
from django.contrib.auth.mixins import LoginRequiredMixin,\
    PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView,\
    DeleteView
from django.views.generic import DetailView, ListView

from .models import Header, Skill


INCLUDE_FOR_EDIT_HEADER = ["name", "category", "description", "cost", "hidden_flag", "skills"]
INCLUDE_FOR_EDIT_SKILL = ["name", "tag", "description", "attention_flag", "bgs_flag"]

class HeaderCreateView(PermissionRequiredMixin, CreateView):
    """
    Allows the Creation of a header.
    """

    model = Header
    fields = INCLUDE_FOR_EDIT_HEADER
    permission_required = ('headers.can_edit', )
    success_url = reverse_lazy('skills:header_list')


class HeaderUpdateView(PermissionRequiredMixin, UpdateView):
    """
    Edits a header that has already been created.
    """

    model = Header
    fields = INCLUDE_FOR_EDIT_HEADER
    permission_required = ('headers.can_edit', )
    success_url = reverse_lazy('skills:header_list')

class HeaderDeleteView(PermissionRequiredMixin, DeleteView):
    """
    Removes a header permanantly.

    Removing a header may have strange effects on characters with that header.
    Removing a header will also remove skills under that header.
    """

    model = Header
    permission_required = ('headers.can_edit', )
    success_url = reverse_lazy('skills:header_list')


class HeaderDetailView(LoginRequiredMixin, DetailView):
    """
    Show the details for a header.
    """

    model = Header
    fields = '__all__'


class HeaderListView(LoginRequiredMixin, ListView):
    """
    List headers.

    Should not show hidden headers to user who are not allowed to see them.
    Provides links to the details for a header, for editing a header and for adding
    skills to a header.
    """

    model = Header
    paginate_by = 25

class SkillCreateView(PermissionRequiredMixin, CreateView):
    """
    Allows the creation of a skill.
    """

    model = Skill
    fields = INCLUDE_FOR_EDIT_SKILL
    permission_required = ('skills.can_edit', )
    success_url = reverse_lazy('skills:skill_list')


class SkillUpdateView(PermissionRequiredMixin, UpdateView):
    """
    Edits a skill that has already been created.
    """

    model = Skill
    fields = INCLUDE_FOR_EDIT_SKILL
    permission_required = ('skills.can_edit', )
    success_url = reverse_lazy('skills:skill_list')

class SkillDeleteView(PermissionRequiredMixin, DeleteView):
    """
    Removes a skill permanantly.

    Removing a skill may have strange effects on characters with that skill.
    """

    model = Skill
    permission_required = ('skills.can_edit', )
    success_url = reverse_lazy('skills:skill_list')


class SkillDetailView(LoginRequiredMixin, DetailView):
    """
    Show the details for a skill.
    """

    model = Skill
    fields = '__all__'


class SkillListView(LoginRequiredMixin, ListView):
    """
    List skills.

    Should not show hidden skills to user who are not allowed to see them.
    Provides links to the details for a skill, for editing a skill.
    """

    model = Skill
    paginate_by = 25
