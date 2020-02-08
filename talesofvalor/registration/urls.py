"""Router for views for events."""
from django.urls import path, re_path

from .views import RegistrationSendView, RegistrationCompleteView

app_name = 'registration'

urlpatterns = [
    path(
        'send/',
        RegistrationSendView.as_view(),
        name='create'
    ),    
   	path(
        'complete/<int:pk>/',
        RegistrationCompleteView.as_view(),
        name='complete'
    ),
]
