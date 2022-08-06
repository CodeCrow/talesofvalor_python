"""Router for views for characters."""
from django.urls import path

from .views import BetweenGameSkillCreateView, BetweenGameSkillUpdateView,\
    BetweenGameSkillDetailView, BetweenGameSkillListView,\
    BetweenGameSkillDeleteView, BetweenGameSkillCharacterEventView

app_name = 'betweengameskills'

urlpatterns = [
    path(
        '<int:event_id>',
        BetweenGameSkillListView.as_view(),
        name='betweengameskill_list'
    ),
    path(
        'add/',
        BetweenGameSkillCreateView.as_view(),
        name='betweengameskill_create'
    ),
    path(
        '<int:pk>/',
        BetweenGameSkillDetailView.as_view(),
        name='betweengameskill_detail'
    ),
    path(
        '<int:pk>/edit/',
        BetweenGameSkillUpdateView.as_view(),
        name='betweengameskill_update'
    ),
    path(
        '<int:pk>/delete/',
        BetweenGameSkillDeleteView.as_view(),
        name='betweengameskill_delete'
    ),
    path(
        'event/<int:event_id>/character/<int:character_id>/',
        BetweenGameSkillCharacterEventView.as_view(),
        name='betweengameskillcharacterevent_detail'
    )
]
