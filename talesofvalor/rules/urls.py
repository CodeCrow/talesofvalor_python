"""Router for views for characters."""
from django.conf.urls import url

from .views import RuleCreateView, RuleUpdateView,\
    RuleDetailView, RuleListView, RuleDeleteView

urlpatterns = [
    url(
        r'^$',
        RuleListView.as_view(),
        name='rule_list'
    ),
    url(
        r'^add/?$',
        RuleCreateView.as_view(),
        name='rule_create'
    ),
    url(
        r'^(?P<pk>[0-9]+)/?$',
        RuleDetailView.as_view(),
        name='rule_detail'
    ),
    url(
        r'^(?P<pk>[0-9]+)/edit/?$',
        RuleUpdateView.as_view(),
        name='rule_update'
    ),
    url(
        r'^(?P<pk>[0-9]+)/delete/?$',
        RuleDeleteView.as_view(),
        name='rule_delete'
    )
]
