"""Router for views for characters."""
from django.conf.urls import url

from .views import CharacterCreateView, CharacterUpdateView,\
    CharacterDetailView, CharacterDeleteView, CharacterListView,\
    CharacterSetActiveView, CharacterSkillUpdateView

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
        r'^(?P<pk>[0-9]+)/delete/?$',
        CharacterDeleteView.as_view(),
        name='character_delete'
    ),
    url(
        r'^(?P<pk>[0-9]+)/update/?$',
        CharacterUpdateView.as_view(),
        name='character_update'
    ),
    url(
        r'^(?P<pk>[0-9]+)/skill/?$',
        CharacterSkillUpdateView.as_view(),
        name='character_skill_update'
    ),
    url(
        r'^(?P<pk>[0-9]+)/setactive/?$',
        CharacterSetActiveView.as_view(),
        name='character_set_active'
    ),
    url(
        r'$',
        CharacterListView.as_view(),
        name='character_list'
    ),
]
