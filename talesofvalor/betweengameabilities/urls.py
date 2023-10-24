"""Router for views for characters."""
from django.urls import path

from .views import BetweenGameAbilityCreateView, BetweenGameAbilityUpdateView,\
    BetweenGameAbilityDetailView, BetweenGameAbilityListView,\
    BetweenGameAbilityDeleteView

app_name = 'betweengameabilities'

urlpatterns = [
    path(
        '<int:event_id>',
        BetweenGameAbilityListView.as_view(),
        name='betweengameability_list'
    ),
    path(
        '',
        BetweenGameAbilityListView.as_view(),
        name='betweengameability_list'
    ),
    path(
        'add/',
        BetweenGameAbilityCreateView.as_view(),
        name='betweengameability_create'
    ),
    path(
        '<int:pk>/',
        BetweenGameAbilityDetailView.as_view(),
        name='betweengameability_detail'
    ),
    path(
        '<int:pk>/edit/',
        BetweenGameAbilityUpdateView.as_view(),
        name='betweengameability_update'
    ),
    path(
        '<int:pk>/delete/',
        BetweenGameAbilityDeleteView.as_view(),
        name='betweengameability_delete'
    )
]
