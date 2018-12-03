"""Router for views for characters."""
from django.conf.urls import url

from .views import BetweenGameSkillCreateView, BetweenGameSkillUpdateView,\
    BetweenGameSkillDetailView, BetweenGameSkillListView,\
    BetweenGameSkillDeleteView

urlpatterns = [
    url(
        r'^$',
        BetweenGameSkillListView.as_view(),
        name='betweengameskill_list'
    ),
    url(
        r'^add/?$',
        BetweenGameSkillCreateView.as_view(),
        name='betweengameskill_create'
    ),
    url(
        r'^(?P<pk>[0-9]+)/?$',
        BetweenGameSkillDetailView.as_view(),
        name='betweengameskill_detail'
    ),
    url(
        r'^(?P<pk>[0-9]+)/edit/?$',
        BetweenGameSkillUpdateView.as_view(),
        name='betweengameskill_update'
    ),
    url(
        r'^(?P<pk>[0-9]+)/delete/?$',
        BetweenGameSkillDeleteView.as_view(),
        name='betweengameskill_delete'
    )
]
