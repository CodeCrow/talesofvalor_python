"""Router for views for attendance."""
from django.conf.urls import url

from .views import AttendanceCreateView, AttendanceUpdateView,\
    AttendanceListView, AttendanceDetailView, AttendanceDeleteView

urlpatterns = [
    url(
        r'^add/?$',
        AttendanceCreateView.as_view(),
        name='attendance_create'
    ),
    url(
        r'^(?P<pk>[0-9]+)/update/?$',
        AttendanceUpdateView.as_view(),
        name='attendance_update'
    ),
    url(
        r'^(?P<pk>[0-9]+)/?$',
        AttendanceDetailView.as_view(),
        name='attendance_detail'
    ),
    url(
        r'^(?P<pk>[0-9]+)/delete/?$',
        AttendanceDeleteView.as_view(),
        name='attendance_delete'
    ),
    url(
        r'$',
        AttendanceListView.as_view(),
        name='attendance_list'
    ),
]
