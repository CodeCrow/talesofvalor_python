"""Router for views for players."""
from django.urls import path

from .views import PlayerUpdateView,\
    PlayerRedirectDetailView, PlayerDetailView, RegistrationView,\
    PlayerListView, PlayerDeleteView, PlayerViewSet, MassEmailView,\
    PlayerListRegistrationView, PlayerListAttendanceView,\
    MassGrantCPView,\
    PELListView, PELCreateView, PELDetailView, PELRedirectView, PELUpdateView

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
        'home/',
        PlayerRedirectDetailView.as_view(),
        name='player_redirect_detail'
    ), 
    path(
        'pel/',
        PELListView.as_view(),
        name='pel_list'
    ),
    path(
        'pel/<int:pk>/',
        PELDetailView.as_view(),
        name='pel_detail'
    ),    
    path(
        'pel/<int:character_id>/<int:event_id>/',
        PELRedirectView.as_view(),
        name='pel_redirect'
    ),
    path(
        'pel/<int:pk>/edit',
        PELUpdateView.as_view(),
        name='pel_update'
    ),   
    path(
        'pel/add/<int:character_id>/<int:event_id>/',
        PELCreateView.as_view(),
        name='pel_create'
    ),
    path(
        '<int:pk>/',
        PlayerDetailView.as_view(),
        name='player_detail'
    ),
    path(
        '<int:pk>/update/',
        PlayerUpdateView.as_view(),
        name='player_update'
    ),
    path(
        '<int:pk>/delete/',
        PlayerDeleteView.as_view(),
        name='player_delete'
    ),
    path(
        '',
        PlayerListView.as_view(),
        name='player_list'
    ),
]
