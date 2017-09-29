"""Router for views for players."""
from django.conf.urls import url

from .views import PlayerCreateView, PlayerUpdateView, RegistrationView

urlpatterns = [
    url(
        r'^register/?$',
        RegistrationView.as_view(),
        name='registration'
    ),
    url(
        r'^add/?$',
        PlayerCreateView.as_view(),
        name='player_create'
    ),
    url(
        r'^(?P<username>[-\w]+)/update/?$',
        PlayerUpdateView.as_view(),
        name='player_update'
    ),
]
