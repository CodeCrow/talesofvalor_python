"""Router for views for players."""
from django.conf.urls import url

from .views import PlayerCreateView, PlayerUpdateView

urlpatterns = [
    url(
        r'^add/?$',
        PlayerCreateView.as_view(),
        name='player_create'
    ),
    url(
        r'^(?P<username>[-\w]+)/?$',
        PlayerUpdateView.as_view(),
        name='player_update'
    ),
]
