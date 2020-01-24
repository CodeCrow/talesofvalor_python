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
from django.views.generic.edit import CreateView, UpdateView,\
    DeleteView
from django.urls import reverse_lazy

from .forms import RuleForm
from .models import Rule


class RuleCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Rule
    permission_required = ('rules.create_rule', )
    success_url = reverse_lazy('rules:rule_list')

    template_name = 'rules/rule_form.html'
    form_class = RuleForm


class RuleUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Rule
    permission_required = ('rules.change_rule', )
    success_url = reverse_lazy('rules:rule_list')

    template_name = 'rules/rule_form.html'
    form_class = RuleForm


class RuleDeleteView(PermissionRequiredMixin, DeleteView):
    """
    Removes a rule permanantly.

    Removing a rule may have strange effects on characters with skill grants or 
    skill cost changes as a result of that rule.
    """

    model = Rule
    permission_required = ('rules.change_rule', )
    success_url = reverse_lazy('rules:rule_list')


class RuleDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    """Show the details for a rule."""

    model = Rule
    fields = '__all__'
    permission_required = ('rules.change_rule', )

class RuleListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """
    Lists the rules.

    A list of the rules currently in play.
    """

    model = Rule
    permission_required = ('rules.change_rule', )