"""Router for views for characters."""
from django.conf.urls import url

from .views import CharacterCreateView, CharacterUpdateView, CharacterDetailView

urlpatterns = [
    url(
        r'^add/?$',
        CharacterCreateView.as_view(),
        name='character_create'
    ),
    url(
        r'^(?P<pk>[0-9]+)/?$',
        CharacterDetailView.as_view(),
        name='character_detail'
    ),
    url(
        r'^(?P<pk>[0-9]+)/edit/?$',
        CharacterUpdateView.as_view(),
        name='character_update'
    ),
]
