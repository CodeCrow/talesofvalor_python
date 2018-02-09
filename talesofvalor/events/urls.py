"""Router for views for events."""
from django.conf.urls import url

from .views import EventCreateView, EventUpdateView, EventListView,\
    EventDetailView

urlpatterns = [
    url(
        r'^add/?$',
        EventCreateView.as_view(),
        name='event_create'
    ),
    url(
        r'^(?P<pk>[0-9]+)/update?$',
        EventUpdateView.as_view(),
        name='event_update'
    ),
    url(
        r'^(?P<pk>[0-9]+)/?$',
        EventDetailView.as_view(),
        name='event_detail'
    ),
    url(
        r'$',
        EventListView.as_view(),
        name='event_list'
    ),
]
