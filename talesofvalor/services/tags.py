"""
Services related to tags and tagging through Taggit
"""
from dal import autocomplete

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.list import ListView

from taggit.models import Tag


class TagsAutocompleteView(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self):

        qs = Tag.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs

    def get_create_option(self, context, q):
        return []


class TagListView(PermissionRequiredMixin, ListView):
    """
    List the items associated with a specific tag.
    """
    model = Tag
    permission_required = ('players.view_any_player', )
    template_name = "services/tag_list.html"

    def get_queryset(self):
        qs = super().get_queryset()
        slug = self.kwargs.get('tag')
        if slug:
            qs = qs.filter(slug=self.kwargs.get('tag'))
        return qs
