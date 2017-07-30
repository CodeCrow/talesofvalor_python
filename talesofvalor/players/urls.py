"""Router for views for players."""
from django.conf.urls import url

from .views import PlayerCreateView

urlpatterns = [
    url(
        r'^(?P<username>[-\w]+)/$',
        PlayerCreateView.as_view(),
        name='player_create'
    ),
]
