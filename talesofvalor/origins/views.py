"""
These are views that are used for viewing and editing origins.

Origins function as backgrounds for characters and are mechanically equivalent.
"""
from django.contrib.auth.mixins import LoginRequiredMixin,\
    PermissionRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView,\
    DeleteView
from django.views.generic import DetailView, ListView

from .models import Origin

INCLUDE_FOR_EDIT = ["name", "type", "description"]

class OriginCreateView(PermissionRequiredMixin, CreateView):
    """
    Allows the Creation of an origin
    """

    model = Origin
    fields = INCLUDE_FOR_EDIT
    permission_required = ('origins.can_edit', )
    success_url = reverse_lazy('origins:origin_list')


class OriginUpdateView(PermissionRequiredMixin, UpdateView):
    """
    Edits and origin that has already been created
    """

    model = Origin
    fields = INCLUDE_FOR_EDIT
    permission_required = ('origins.can_edit', )
    success_url = reverse_lazy('origins:origin_list')

class OriginDeleteView(PermissionRequiredMixin, DeleteView):
    """
    Removes an origin permanantly.

    Removing an origin may have strange effects on characters with that origin.
    """

    model = Origin
    permission_required = ('origins.can_edit', )
    success_url = reverse_lazy('origins:origin_list')


class OriginDetailView(LoginRequiredMixin, DetailView):
    """
    Show the details for a character.

    From here you can edit the details of a character or choose skills.
    """

    model = Origin
    fields = '__all__'


class OriginListView(LoginRequiredMixin, ListView):
    """
    Show the details for a character.

    From here you can edit the details of a character or choose skills.
    """

    model = Origin
    paginate_by = 25
