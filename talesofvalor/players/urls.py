"""Router for views for players."""
from django.conf.urls import url

from .views import PlayerCreateView, PlayerUpdateView,\
    PlayerRedirectDetailView, PlayerDetailView, RegistrationView,\
    PlayerListView, PlayerDeleteView, PlayerViewSet, MassEmailView,\
    PlayerListRegistrationView, PlayerListAttendanceView

urlpatterns = [
    url(
        r'^mail/$',
        MassEmailView.as_view(),
        name='player_mail'
    ),
    url(
        r'^select/$',
        PlayerViewSet.as_view(),
        name='player_select'
    ),
    url(
        r'^register/mass/?$',
        PlayerListRegistrationView.as_view(),
        name='player_mass_registration'
    ),
    url(
        r'^attendance/mass/?$',
        PlayerListAttendanceView.as_view(),
        name='player_mass_attendance'
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
