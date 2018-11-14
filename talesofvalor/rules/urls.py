"""Router for views for characters."""
from django.conf.urls import url

from .views import RulesCreateView, RulesUpdateView,\
    RulesDetailView, RulesListView, RulesDeleteView

urlpatterns = [
    url(
        r'^$',
        RulesListView.as_view(),
        name='rules_list'
    ),
    url(
        r'^add/?$',
        RulesCreateView.as_view(),
        name='rules_create'
    ),
    url(
        r'^(?P<pk>[0-9]+)/?$',
        RulesDetailView.as_view(),
        name='rules_detail'
    ),
    url(
        r'^(?P<pk>[0-9]+)/edit/?$',
        RuleUpdateView.as_view(),
        name='rules_update'
    ),
    url(
        r'^(?P<pk>[0-9]+)/delete/?$',
        RuleDeleteView.as_view(),
        name='rules_delete'
    )
]
