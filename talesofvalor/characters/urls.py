"""Router for views for characters."""
from django.urls import path

from .views import CharacterCreateView, CharacterUpdateView,\
    CharacterDetailView, CharacterDeleteView, CharacterResetView,\
    CharacterListView, CharacterPrintListView,\
    CharacterSetActiveView, CharacterSkillUpdateView,\
    CharacterConceptApproveView, CharacterHistoryApproveView,\
    ResetPointsView,\
    CharacterAddHeaderView, CharacterDropHeaderView, CharacterAddSkillView,\
    CharacterInfluenceUpdateListView

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
        '<int:pk>/reset/',
        CharacterResetView.as_view(),
        name='character_reset'
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
        'approveconcept/',
        CharacterConceptApproveView.as_view(),
        name='concept_approve'
    ),
    path(
        'approvehistory/',
        CharacterHistoryApproveView.as_view(),
        name='history_approve'
    ),
    path(
        '',
        CharacterListView.as_view(),
        name='character_list'
    ),
    path(
        'print/<int:event_id>/',
        CharacterPrintListView.as_view(),
        name='character_print_list'
    ),
    path(
        'print/',
        CharacterPrintListView.as_view(),
        name='character_print_list'
    ),
    path(
        'reset_points/',
        ResetPointsView.as_view(),
        name='reset_points'
    ),
    # skill picking
    path(
        'addheader/',
        CharacterAddHeaderView.as_view(),
        name='header_add'
    ),
    path(
        'dropheader/',
        CharacterDropHeaderView.as_view(),
        name='header_drop'
    ),
    path(
        'addskill/',
        CharacterAddSkillView.as_view(),
        name='skill_add'
    ),
    # influence
    path(
        'influence/<int:event_id>/',
        CharacterInfluenceUpdateListView.as_view(),
        name='influence_list'
    ),
    path(
        'influence/',
        CharacterInfluenceUpdateListView.as_view(),
        name='influence_list'
    )
]
