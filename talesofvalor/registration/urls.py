"""Router for views for events."""
from django.urls import path

from .views import RegistrationSendView

app_name = 'registration'

urlpatterns = [
    path(
        'send/',
        RegistrationSendView.as_view(),
        name='create'
    ),
]
