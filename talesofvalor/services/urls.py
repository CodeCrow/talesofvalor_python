"""Router for services not specific to apps"""
from django.urls import path

from .tags import TagsAutocompleteView

app_name = 'services'

urlpatterns = [
    path(
        'tags/suggest/',
        TagsAutocompleteView.as_view(),
        name='tag_autocomplete'
    ),
]
