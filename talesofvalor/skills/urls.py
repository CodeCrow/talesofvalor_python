"""Router for views for characters."""
from django.conf.urls import url

from .views import HeaderCreateView, HeaderUpdateView,\
    HeaderDetailView, HeaderListView, HeaderDeleteView,\
    SkillCreateView, SkillUpdateView, SkillTreeView,\
    SkillDetailView, SkillListView, SkillDeleteView

urlpatterns = [
    url(
        r'^headers/?$',
        HeaderListView.as_view(),
        name='header_list'
    ),
    url(
        r'^headers/add/?$',
        HeaderCreateView.as_view(),
        name='header_create'
    ),
    url(
        r'^headers/(?P<pk>[0-9]+)/?$',
        HeaderDetailView.as_view(),
        name='header_detail'
    ),
    url(
        r'^headers/(?P<pk>[0-9]+)/edit/?$',
        HeaderUpdateView.as_view(),
        name='header_update'
    ),
    url(
        r'^headers/(?P<pk>[0-9]+)/delete/?$',
        HeaderDeleteView.as_view(),
        name='header_delete'
    ),
    url(
        r'^$',
        SkillListView.as_view(),
        name='skill_list'
    ),
    url(
        r'^tree/$',
        SkillTreeView.as_view(),
        name='skill_tree'
    ),
    url(
        r'^add/?$',
        SkillCreateView.as_view(),
        name='skill_create'
    ),
    url(
        r'^(?P<pk>[0-9]+)/?$',
        SkillDetailView.as_view(),
        name='skill_detail'
    ),
    url(
        r'^(?P<pk>[0-9]+)/edit/?$',
        SkillUpdateView.as_view(),
        name='skill_update'
    ),
    url(
        r'^(?P<pk>[0-9]+)/delete/?$',
        SkillDeleteView.as_view(),
        name='skill_delete'
    ),
]
