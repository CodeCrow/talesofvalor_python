"""Router for views for players."""
from django.conf.urls import url

from .views import PlayerCreateView, PlayerUpdateView,\
    PlayerRedirectDetailView, PlayerDetailView, RegistrationView,\
    PlayerListView, PlayerDeleteView, PlayerViewSet

urlpatterns = [
    url(
        r'^select/$',
        PlayerViewSet.as_view(),
        name='player_select'
    ),
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
        r'^home/?$',
        PlayerRedirectDetailView.as_view(),
        name='player_redirect_detail'
    ),
    url(
        r'^(?P<username>[-\w]+)/?$',
        PlayerDetailView.as_view(),
        name='player_detail'
    ),
    url(
        r'^(?P<username>[-\w]+)/update/?$',
        PlayerUpdateView.as_view(),
        name='player_update'
    ),
    url(
        r'^(?P<username>[-\w]+)/delete/?$',
        PlayerDeleteView.as_view(),
        name='player_delete'
    ),
    url(
        r'^$',
        PlayerListView.as_view(),
        name='player_list'
    ),
]
