"""Router for views for characters."""
from django.conf.urls import url

from .views import CharacterCreateView, CharacterUpdateView

urlpatterns = [
    url(
        r'^add/?$',
        CharacterCreateView.as_view(),
        name='character_create'
    ),
    url(
        r'^(?P<pk>[0-9]+)/?$',
        CharacterUpdateView.as_view(),
        name='character_update'
    ),
]
