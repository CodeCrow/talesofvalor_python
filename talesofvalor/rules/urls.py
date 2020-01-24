"""Router for views for characters."""
from django.urls import path

from .views import RuleCreateView, RuleUpdateView,\
    RuleDetailView, RuleListView, RuleDeleteView

app_name = 'rules'

urlpatterns = [
    path(
        '',
        RuleListView.as_view(),
        name='rule_list'
    ),
    path(
        'add/',
        RuleCreateView.as_view(),
        name='rule_create'
    ),
    path(
        '<int:pk>/',
        RuleDetailView.as_view(),
        name='rule_detail'
    ),
    path(
        '<int:pk>/edit/',
        RuleUpdateView.as_view(),
        name='rule_update'
    ),
    path(
        '<int:pk>/delete/',
        RuleDeleteView.as_view(),
        name='rule_delete'
    )
]
