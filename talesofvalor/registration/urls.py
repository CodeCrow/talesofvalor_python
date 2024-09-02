"""Router for views for events."""
from django.urls import path, re_path

from .views import RegistrationSendView, RegistrationCompleteView,\
    RegistrationDetailView, RegistrationUpdateView,\
    RegistrationRequestListView, RegistrationRequestApproveFormView,\
    RegistrationRequestDenyFormView,\
    RegistrationRequestDetailView, RegistrationListView,\
    RegistrationRequestAlreadyPaidView, RegistrationRequestPayAtDoorView,\
    RegistrationRequestDeleteView

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
    path(
        '<int:pk>/edit/',
        RegistrationUpdateView.as_view(),
        name='edit'
    ),
    re_path(
        'event/(?P<event>[0-9]+)/((?P<player>[0-9]+)/)?',
        RegistrationListView.as_view(),
        name='list'
    ),
    path(
        'request/<int:pk>/alreadypaid/',
        RegistrationRequestAlreadyPaidView.as_view(),
        name='request_already_paid'
    ),
    path(
        'request/<int:pk>/approve/',
        RegistrationRequestApproveFormView.as_view(),
        name='request_approve'
    ),
    path(
        'request/<int:pk>/deny/',
        RegistrationRequestDenyFormView.as_view(),
        name='request_deny'
    ),
    path(
        'request/<int:pk>/payatdoor/',
        RegistrationRequestPayAtDoorView.as_view(),
        name='request_pay_at_door'
    ),
    path(
        'request/<int:pk>/delete/',
        RegistrationRequestDeleteView.as_view(),
        name='request_delete'
    ),   
    path(
        'request/<int:pk>/',
        RegistrationRequestDetailView.as_view(),
        name='request_detail'
    ),
    path(
        'request/',
        RegistrationRequestListView.as_view(),
        name='request_list'
    ),
]
