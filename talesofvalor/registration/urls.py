"""Router for views for events."""
from django.urls import path

from .views import RegistrationSendView, RegistrationCompleteView,\
    RegistrationDetailView

app_name = 'registration'

urlpatterns = [
    path(
        'send/',
        RegistrationSendView.as_view(),
        name='create'
    ),
    path(
        'complete/',
        RegistrationCompleteView.as_view(),
        name='complete'
    ),
    path(
        '<int:pk>/',
        RegistrationDetailView.as_view(),
        name='detail'
    ),
]
