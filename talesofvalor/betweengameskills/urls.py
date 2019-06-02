"""Router for views for characters."""
from django.conf.urls import url

from .views import BetweenGameSkillCreateView, BetweenGameSkillUpdateView,\
    BetweenGameSkillDetailView, BetweenGameSkillListView,\
    BetweenGameSkillDeleteView, BetweenGameSkillCharacterEventView

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
    ),
    url(
        r'^event/(?P<event_id>[0-9]+)/character/(?P<character_id>[0-9]+)/?$',
        BetweenGameSkillCharacterEventView.as_view(),
        name='betweengameskillcharacterevent_detail'
    )
]
