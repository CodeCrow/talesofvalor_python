"""Router for views for events."""
from django.conf.urls import url

from .views import EventCreateView, EventUpdateView

urlpatterns = [
    url(
        r'^add/?$',
        EventCreateView.as_view(),
        name='event_create'
    ),
    url(
        r'^(?P<pk>[0-9]+)/?$',
        EventUpdateView.as_view(),
        name='event_update'
    ),
]
