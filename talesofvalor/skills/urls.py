"""Router for views for characters."""
from django.urls import path

from .views import HeaderCreateView, HeaderUpdateView,\
    HeaderDetailView, HeaderListView, HeaderDeleteView,\
    SkillCreateView, SkillUpdateView, SkillTreeView,\
    SkillDetailView, SkillListView, SkillDeleteView,\
    SkillSearchView

app_name = "skills"

urlpatterns = [
    path(
        'headers/',
        HeaderListView.as_view(),
        name='header_list'
    ),
    path(
        'headers/add/',
        HeaderCreateView.as_view(),
        name='header_create'
    ),
    path(
        'headers/<int:pk>/',
        HeaderDetailView.as_view(),
        name='header_detail'
    ),
    path(
        'headers/<int:pk>/edit/',
        HeaderUpdateView.as_view(),
        name='header_update'
    ),
    path(
        'headers/<int:pk>/delete/',
        HeaderDeleteView.as_view(),
        name='header_delete'
    ),
    path(
        '',
        SkillListView.as_view(),
        name='skill_list'
    ),
    path(
        'tree/',
        SkillTreeView.as_view(),
        name='skill_tree'
    ),
    path(
        'add/',
        SkillCreateView.as_view(),
        name='skill_create'
    ),
    path(
        '<int:pk>/',
        SkillDetailView.as_view(),
        name='skill_detail'
    ),
    path(
        '<int:pk>/edit/',
        SkillUpdateView.as_view(),
        name='skill_update'
    ),
    path(
        '<int:pk>/delete/',
        SkillDeleteView.as_view(),
        name='skill_delete'
    ),
    path(
        'api/<str:criteria>/',
        SkillSearchView.as_view(),
        name='skill_search'
    )
]
