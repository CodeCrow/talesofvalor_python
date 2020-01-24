"""Router for views for characters."""
from django.urls import path

from .views import OriginCreateView, OriginUpdateView,\
    OriginDetailView, OriginListView, OriginDeleteView,\
    OriginAddSkillView

app_name = 'origins'

urlpatterns = [
    path(
        '',
        OriginListView.as_view(),
        name='origin_list'
    ),
    path(
        'add/',
        OriginCreateView.as_view(),
        name='origin_create'
    ),
    path(
        '<int:pk>/',
        OriginDetailView.as_view(),
        name='origin_detail'
    ),
    path(
        '<int:pk>/edit/',
        OriginUpdateView.as_view(),
        name='origin_update'
    ),
    path(
        '<int:pk>/delete/',
        OriginDeleteView.as_view(),
        name='origin_delete'
    ),
    path(
        '<int:pk>/addskill/',
        OriginAddSkillView.as_view(),
        name='origin_addskill'
    )
]
