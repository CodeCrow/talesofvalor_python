"""Different reports for events."""
from django.urls import path

from .views import DiningReportListView, RegistrationReportListView

app_name = "reports"

urlpatterns = [
    path(
        'dining/<int:event_id>/',
        DiningReportListView.as_view(),
        name='dining'
    ),
    path(
        'dining/',
        DiningReportListView.as_view(),
        name='dining'
    ),
    path(
        'registration/<int:event_id>/',
        RegistrationReportListView.as_view(),
        name='registration'
    ),
    path(
        'registration/',
        RegistrationReportListView.as_view(),
        name='registration'
    )
]
