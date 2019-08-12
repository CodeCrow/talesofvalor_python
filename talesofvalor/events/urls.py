"""Router for views for events."""
from django.urls import path

from .views import EventCreateView, EventUpdateView, EventListView,\
    EventDetailView, PlayerRegistrationView

app_name = 'events'

urlpatterns = [
    path(
        'add/',
        EventCreateView.as_view(),
        name='event_create'
    ),
    path(
        '<int:pk>/update/',
        EventUpdateView.as_view(),
        name='event_update'
    ),
    path(
        '<int:pk>/',
        EventDetailView.as_view(),
        name='event_detail'
    ),
    path(
        'char/<int:character>/',
        EventListView.as_view(),
        name='event_list'
    ),
    path(
        '',
        EventListView.as_view(),
        name='event_list'
    ),
    path(
        '<int:pk>/register/',
        PlayerRegistrationView.as_view(),
        name='register'
    ),
]
