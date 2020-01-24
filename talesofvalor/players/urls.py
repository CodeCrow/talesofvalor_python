"""Router for views for players."""
from django.urls import path

from .views import PlayerCreateView, PlayerUpdateView,\
    PlayerRedirectDetailView, PlayerDetailView, RegistrationView,\
    PlayerListView, PlayerDeleteView, PlayerViewSet, MassEmailView,\
    PlayerListRegistrationView, PlayerListAttendanceView,\
    MassGrantCPView

app_name = 'players'

urlpatterns = [
    path(
        'mail/',
        MassEmailView.as_view(),
        name='player_mail'
    ),
    path(
        'massgrantcps/',
        MassGrantCPView.as_view(),
        name='player_mass_grantcp'
    ),
    path(
        'select/',
        PlayerViewSet.as_view(),
        name='player_select'
    ),
    path(
        'register/mass/',
        PlayerListRegistrationView.as_view(),
        name='player_mass_registration'
    ),
    path(
        'attendance/mass/',
        PlayerListAttendanceView.as_view(),
        name='player_mass_attendance'
    ),
    path(
        'register/',
        RegistrationView.as_view(),
        name='registration'
    ),
    path(
        'add/',
        PlayerCreateView.as_view(),
        name='player_create'
    ),
    path(
        'home/',
        PlayerRedirectDetailView.as_view(),
        name='player_redirect_detail'
    ),
    path(
        '<slug:username>/',
        PlayerDetailView.as_view(),
        name='player_detail'
    ),
    path(
        '<slug:username>/update/',
        PlayerUpdateView.as_view(),
        name='player_update'
    ),
    path(
        '<slug:username>/delete/',
        PlayerDeleteView.as_view(),
        name='player_delete'
    ),
    path(
        '',
        PlayerListView.as_view(),
        name='player_list'
    ),
]
