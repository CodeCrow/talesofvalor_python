"""
These are views that are used for viewing and editing origins.

Origins function as backgrounds for characters and are mechanically equivalent.
"""
from django.contrib.auth.mixins import LoginRequiredMixin,\
    PermissionRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView,\
    DeleteView
from django.views.generic import DetailView, ListView

from .models import Origin
from .forms import RuleFormSet

INCLUDE_FOR_EDIT = ["name", "type", "description"]


class OriginCreateView(PermissionRequiredMixin, CreateView):
    """
    Allows the Creation of an origin
    """
    model = Origin
    fields = INCLUDE_FOR_EDIT
    permission_required = ('origins.add_origin', )
    success_url = reverse_lazy('origins:origin_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['rule_formset'] = RuleFormSet(self.request.POST)
        else:
            context['rule_formset'] = RuleFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        rule_formset = context['rule_formset']
        if rule_formset.is_valid():
            self.object = form.save()
            rule_formset.instance = self.object
            rule_formset.save()
        else:
            return self.render_to_response(self.get_context_data(form=form))
        return redirect(self.success_url)


class OriginUpdateView(PermissionRequiredMixin, UpdateView):
    """
    Edits an origin that has already been created
    """

    model = Origin
    fields = INCLUDE_FOR_EDIT
    permission_required = ('origins.change_origin', )
    success_url = reverse_lazy('origins:origin_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['rule_formset'] = RuleFormSet(self.request.POST, instance=self.object)
            context['rule_formset'].full_clean()
        else:
            context['rule_formset'] = RuleFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        rule_formset = context['rule_formset']
        if rule_formset.is_valid():
            self.object = form.save()
            rule_formset.instance = self.object
            rule_formset.save()
        else:
            return self.render_to_response(self.get_context_data(form=form))
        return redirect(self.success_url)



class OriginDeleteView(PermissionRequiredMixin, DeleteView):
    """
    Removes an origin permanantly.

    Removing an origin may have strange effects on characters with that origin.
    """

    model = Origin
    permission_required = ('origins.delete_origin', )
    success_url = reverse_lazy('origins:origin_list')


class OriginDetailView(DetailView):
    """
    Show the details for an origin.

    From here you can edit the details of a character or choose skills.
    """

    model = Origin
    fields = '__all__'


class OriginListView(LoginRequiredMixin, ListView):
    """
    Show the list of origins.

    From here you will be able to click to add a new origin,
    view, or edit an existing origin.
    """

    model = Origin
    paginate_by = 25
