"""Router for views for attendance."""
from django.urls import path

from .views import AttendanceCreateView, AttendanceUpdateView,\
    AttendanceListView, AttendanceDetailView, AttendanceDeleteView

app_name = 'attendance'

urlpatterns = [
    path(
        'add/',
        AttendanceCreateView.as_view(),
        name='attendance_create'
    ),
    path(
        '<int:pk>/update/',
        AttendanceUpdateView.as_view(),
        name='attendance_update'
    ),
    path(
        '<int:pk>',
        AttendanceDetailView.as_view(),
        name='attendance_detail'
    ),
    path(
        '<int:pk>/delete/',
        AttendanceDeleteView.as_view(),
        name='attendance_delete'
    ),
    path(
        '',
        AttendanceListView.as_view(),
        name='attendance_list'
    ),
]
