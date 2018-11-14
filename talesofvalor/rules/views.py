"""
These are views viewing and editing rules. 

Rules are descriptions of cost changes that are caused by origins, or headers or other character
choices.
"""

from django.contrib.auth.mixins import UserPassesTestMixin,\
    LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login
from django.views.generic import DetailView, ListView
from django.views.generic.base import RedirectView
from django.views.generic.edit import CreateView, UpdateView, FormView
from django.urls import reverse

from .forms import RuleForm


class RuleCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Rules
    fields = '__all__'
    permission_required = ('rules.create_rules', )


class RulesUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Rules
    fields = '__all__'
    permission_required = ('rules.change_rules', )


class RulesDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    """Show the details for a rule."""

    model = Rules
    fields = '__all__'
    permission_required = ('rules.change_rules', )

class RulesListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """
    Lists the rules.

    A list of the rules currently in play.
    """

    model = Rules
    permission_required = ('rules.change_rules', )