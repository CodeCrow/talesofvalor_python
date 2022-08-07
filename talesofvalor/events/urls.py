"""Router for views for events."""
from django.urls import path

from .views import EventCreateView, EventUpdateView, EventListView,\
    EventPastListView, EventCharacterPrintListView,\
    EventDetailView, PlayerRegistrationRedirectView,\
    PlayerRegistrationNoEventView, PlayerRegistrationView,\
    EventRegistrationItemDetailView, EventRegistrationItemListView,\
    EventRegistrationItemCreateView, EventRegistrationItemUpdateView

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
        '<int:pk>/print/',
        EventCharacterPrintListView.as_view(),
        name='event_character_print'
    ),
    path(
        'char/<int:character>/',
        EventListView.as_view(),
        name='event_list'
    ),    
    path(
        'register/',
        PlayerRegistrationRedirectView.as_view(),
        name='redirect_register'
    ),
    path(
        'event_no_next_event/',
        PlayerRegistrationNoEventView.as_view(),
        name='event_no_next_event'
    ),
    path(
        '<int:pk>/register/',
        PlayerRegistrationView.as_view(),
        name='register'
    ),  
    path(
        'past/',
        EventPastListView.as_view(),
        name='event_past_list'
    ),
    path(
        '',
        EventListView.as_view(),
        name='event_list'
    ),
    path(
        'registrationitems/<int:pk>/',
        EventRegistrationItemDetailView.as_view(),
        name='eventregistrationitem_detail'
    ),
    path(
        'registrationitems/',
        EventRegistrationItemListView.as_view(),
        name='eventregistrationitem_list'
    ),
    path(
        'registrationitems/add/',
        EventRegistrationItemCreateView.as_view(),
        name='eventregistrationitem_create'
    ),
    path(
        'registrationitems/<int:pk>/update/',
        EventRegistrationItemUpdateView.as_view(),
        name='eventregistrationitem_update'
    ),
]
