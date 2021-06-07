"""Router for views for characters."""
from django.urls import path

from .views import CharacterCreateView, CharacterUpdateView,\
    CharacterDetailView, CharacterDeleteView, CharacterListView,\
    CharacterSetActiveView, CharacterSkillUpdateView,\
    CharacterAddHeaderView, CharacterAddSkillView

app_name = 'characters'

urlpatterns = [
    path(
        'add/',
        CharacterCreateView.as_view(),
        name='character_create'
    ),
    path(
        '<int:pk>',
        CharacterDetailView.as_view(),
        name='character_detail'
    ),
    path(
        '<int:pk>/delete/',
        CharacterDeleteView.as_view(),
        name='character_delete'
    ),
    path(
        '<int:pk>/update/',
        CharacterUpdateView.as_view(),
        name='character_update'
    ),
    path(
        '<int:pk>/skill/',
        CharacterSkillUpdateView.as_view(),
        name='character_skill_update'
    ),
    path(
        '<int:pk>/setactive/',
        CharacterSetActiveView.as_view(),
        name='character_set_active'
    ),
    path(
        '',
        CharacterListView.as_view(),
        name='character_list'
    ),
    # skill picking
    path(
        'addheader/',
        CharacterAddHeaderView.as_view(),
        name='header_add'
    ),
    path(
        'addskill/',
        CharacterAddSkillView.as_view(),
        name='skill_add'
    ),
]
