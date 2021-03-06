"""Router for views for events."""
from django.urls import path

from .views import EventCreateView, EventUpdateView, EventListView,\
    EventDetailView, PlayerRegistrationRedirectView, PlayerRegistrationView,\
    EventRegistrationItemListView, EventRegistrationItemCreateView,\
    EventRegistrationItemUpdateView

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
        'register/',
        PlayerRegistrationRedirectView.as_view(),
        name='redirect_register'
    ),
    path(
        '<int:pk>/register/',
        PlayerRegistrationView.as_view(),
        name='register'
    ),
    path(
        '',
        EventListView.as_view(),
        name='event_list'
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
