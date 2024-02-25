"""
Services related to tags and tagging through Taggit
"""
from dal import autocomplete

from django.contrib.auth.mixins import LoginRequiredMixin
from taggit.models import Tag


class TagsAutocompleteView(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self):

        qs = Tag.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs

    def get_create_option(self, context, q):
        return []