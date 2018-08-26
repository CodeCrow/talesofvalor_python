"""Router for views for characters."""
from django.conf.urls import url

from .views import OriginCreateView, OriginUpdateView,\
    OriginDetailView, OriginListView, OriginDeleteView,\
    OriginAddSkillView

urlpatterns = [
    url(
        r'^$',
        OriginListView.as_view(),
        name='origin_list'
    ),
    url(
        r'^add/?$',
        OriginCreateView.as_view(),
        name='origin_create'
    ),
    url(
        r'^(?P<pk>[0-9]+)/?$',
        OriginDetailView.as_view(),
        name='origin_detail'
    ),
    url(
        r'^(?P<pk>[0-9]+)/edit/?$',
        OriginUpdateView.as_view(),
        name='origin_update'
    ),
    url(
        r'^(?P<pk>[0-9]+)/delete/?$',
        OriginDeleteView.as_view(),
        name='origin_delete'
    ),
    url(
        r'^(?P<pk>[0-9])/addskill/?$',
        OriginAddSkillView.as_view(),
        name='origin_addskill'
    )
]
