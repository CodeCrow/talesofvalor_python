"""
These are views that are used for viewing and editing headers and skills.
"""
from django.contrib.auth.mixins import LoginRequiredMixin,\
    PermissionRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView,\
    DeleteView

from rest_framework.generics import ListAPIView

from talesofvalor.rules.forms import PrerequisiteFormSet

from .forms import SkillForm, HeaderSkillFormSet, RuleFormSet
from .models import Header, Skill
from .serializers import SkillSerializer

INCLUDE_FOR_EDIT_HEADER = ["name", "category", "description", "cost", "hidden_flag", "open_flag"]
INCLUDE_FOR_EDIT_SKILL = ["name", "tag", "description", "attention_flag", "bgs_flag"]


class HeaderCreateView(PermissionRequiredMixin, CreateView):
    """
    Allows the Creation of a header.
    """

    model = Header
    fields = INCLUDE_FOR_EDIT_HEADER
    permission_required = ('skills.add_header', )
    success_url = reverse_lazy('skills:header_list')

    def get_context_data(self, **kwargs):
        context = super(HeaderCreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['rule_formset'] = RuleFormSet(self.request.POST)
            context['prerequisite_formset'] = PrerequisiteFormSet(self.request.POST)
        else:
            context['rule_formset'] = RuleFormSet()
            context['prerequisite_formset'] = PrerequisiteFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        rule_formset = context['rule_formset']
        prerequisite_formset = context['prerequisite_formset']
        if (
                rule_formset.is_valid() and
                prerequisite_formset.is_valid()
        ):
            self.object = form.save()
            rule_formset.instance = self.object
            rule_formset.save()
            prerequisite_formset.instance = self.object
            prerequisite_formset.save()
            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))


class HeaderUpdateView(PermissionRequiredMixin, UpdateView):
    """
    Edits a header that has already been created.
    """

    model = Header
    fields = INCLUDE_FOR_EDIT_HEADER
    permission_required = ('skills.change_header', )
    success_url = reverse_lazy('skills:header_list')

    def get_context_data(self, **kwargs):
        context = super(HeaderUpdateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['rule_formset'] = RuleFormSet(self.request.POST, instance=self.object)
            context['rule_formset'].full_clean()
            context['prerequisite_formset'] = PrerequisiteFormSet(self.request.POST, instance=self.object)
            context['prerequisite_formset'].full_clean()
        else:
            context['rule_formset'] = RuleFormSet(instance=self.object)
            context['prerequisite_formset'] = PrerequisiteFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        rule_formset = context['rule_formset']
        prerequisite_formset = context['prerequisite_formset']
        if (
                rule_formset.is_valid() and
                prerequisite_formset.is_valid()
        ):
            self.object = form.save()
            rule_formset.instance = self.object
            rule_formset.save()
            prerequisite_formset.instance = self.object
            prerequisite_formset.save()
            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))


class HeaderDeleteView(PermissionRequiredMixin, DeleteView):
    """
    Removes a header permanantly.

    Removing a header may have strange effects on characters with that header.
    Removing a header will also remove skills under that header.
    """

    model = Header
    permission_required = ('skills.delete_header', )
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

    def get_queryset(self):
        filter_args = {}
        name_filter = self.request.GET.get('name', None)
        category_filter = self.request.GET.get('category', None)
        description_filter = self.request.GET.get('description', None)
        hidden_filter = self.request.GET.get('hidden_flag', None)
        if name_filter and len(name_filter):
            filter_args['name__istartswith'] = name_filter
        if category_filter and len(category_filter):
            filter_args['category__istartswith'] = category_filter
        if description_filter and len(description_filter):
            filter_args['description__icontains'] = description_filter
        if hidden_filter and len(hidden_filter):
            filter_args['hidden_flag'] = (int(hidden_filter) == 1)
        queryset = self.model.objects.filter(**filter_args)
        return queryset

class SkillCreateView(PermissionRequiredMixin, CreateView):
    """
    Allows the creation of a skill.
    """

    model = Skill
    form_class = SkillForm
    permission_required = ('skills.add_skill', )
    success_url = reverse_lazy('skills:skill_list')

    def get_context_data(self, **kwargs):
        context = super(SkillCreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['headerskill_formset'] = HeaderSkillFormSet(self.request.POST)
            context['rule_formset'] = RuleFormSet(self.request.POST)
            context['prerequisite_formset'] = PrerequisiteFormSet(self.request.POST)
        else:
            context['headerskill_formset'] = HeaderSkillFormSet()
            context['rule_formset'] = RuleFormSet()
            context['prerequisite_formset'] = PrerequisiteFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        header_formset = context['headerskill_formset']
        rule_formset = context['rule_formset']
        prerequisite_formset = context['prerequisite_formset']
        if (
                header_formset.is_valid() and
                rule_formset.is_valid() and
                prerequisite_formset.is_valid()
        ):
            self.object = form.save()
            header_formset.instance = self.object
            header_formset.save()
            rule_formset.instance = self.object
            rule_formset.save()
            prerequisite_formset.instance = self.object
            prerequisite_formset.save()
            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))

class SkillUpdateView(PermissionRequiredMixin, UpdateView):
    """
    Edits a skill that has already been created.
    """

    model = Skill
    form_class = SkillForm
    permission_required = ('skills.change_skill', )
    success_url = reverse_lazy('skills:skill_list')

    def get_context_data(self, **kwargs):
        context = super(SkillUpdateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['headerskill_formset'] = HeaderSkillFormSet(self.request.POST, instance=self.object)
            context['headerskill_formset'].full_clean()
            context['rule_formset'] = RuleFormSet(self.request.POST, instance=self.object)
            context['rule_formset'].full_clean()
            context['prerequisite_formset'] = PrerequisiteFormSet(self.request.POST, instance=self.object)
            context['prerequisite_formset'].full_clean()
        else:
            context['headerskill_formset'] = HeaderSkillFormSet(instance=self.object)
            context['rule_formset'] = RuleFormSet(instance=self.object)
            context['prerequisite_formset'] = PrerequisiteFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        header_formset = context['headerskill_formset']
        rule_formset = context['rule_formset']
        prerequisite_formset = context['prerequisite_formset']
        if (
                header_formset.is_valid() and
                rule_formset.is_valid() and
                prerequisite_formset.is_valid()
        ):
            self.object = form.save()
            header_formset.instance = self.object
            header_formset.save()
            rule_formset.instance = self.object
            rule_formset.save()
            prerequisite_formset.instance = self.object
            prerequisite_formset.save()
            return redirect(self.success_url)
        else:
            return self.render_to_response(self.get_context_data(form=form))

class SkillDeleteView(PermissionRequiredMixin, DeleteView):
    """
    Removes a skill permanantly.

    Removing a skill may have strange effects on characters with that skill.
    """

    model = Skill
    permission_required = ('skills.delete_skill', )
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

    def get_queryset(self):
        filter_args = {}
        name_filter = self.request.GET.get('name', None)
        description_filter = self.request.GET.get('description', None)
        hidden_filter = self.request.GET.get('hidden_flag', None)
        bgs_filter = self.request.GET.get('bgs_flag', None)
        unlinked_filter = self.request.GET.get('unlinked_flag', None)
        if name_filter and len(name_filter):
            filter_args['name__istartswith'] = name_filter
        if description_filter and len(description_filter):
            filter_args['description__icontains'] = description_filter
        if hidden_filter and len(hidden_filter):
            filter_args['headerskill__header__hidden_flag'] = (int(hidden_filter) == 1)
        if bgs_filter and len(bgs_filter):
            filter_args['bgs_flag'] = (int(bgs_filter) == 1)
        if unlinked_filter:
            filter_args['headerskill__isnull'] = True
        queryset = self.model.objects.filter(**filter_args)
        return queryset


class SkillTreeView(ListView):
    """
    Show Skills with Headers, Grouped by category

    Show a list of headers, grouped by category.

    All headers of a category will appear under that category, then a list of skills under that header.
    """

    model = Header
    fields = '__all__'
    template_name = 'skills/skill_tree.html'

    def get_queryset(self):
        queryset = self.model.objects.all().order_by('category')
        return queryset


'''
API Endpoints for skills
'''


class SkillSearchView(ListAPIView):
    serializer_class = SkillSerializer

    def get_queryset(self):
        criteria = self.request.GET.get('criteria', None)
        if criteria:
            return Skill.objects.filter(name__istartswith=criteria)
        return None


class SkillNamesView(View):
    """
    Get the list of name in a flat JSON list.
    """
    def get(self, request, *args, **kwargs):
        skill_names = list(Skill.objects.all().values_list('name', flat=True).order_by('name'))
        return JsonResponse(skill_names, safe=False)
