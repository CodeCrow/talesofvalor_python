"""Router for services not specific to apps"""
from django.urls import path

from .tags import TagsAutocompleteView, TagListView

app_name = 'services'

urlpatterns = [
    path(
        'tags/suggest/',
        TagsAutocompleteView.as_view(),
        name='tag_autocomplete'
    ),
    path(
        'tags/<str:tag>',
        TagListView.as_view(),
        name='tag_list'
    ),
    path(
        'tags/',
        TagListView.as_view(),
        name='tag_list'
    ),
]
