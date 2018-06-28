"""Router for views for characters."""
from django.conf.urls import url

from .views import HeaderCreateView, HeaderUpdateView,\
    HeaderDetailView, HeaderListView, HeaderDeleteView

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
        r'headers/^(?P<pk>[0-9]+)/?$',
        HeaderDetailView.as_view(),
        name='header_detail'
    ),
    url(
        r'headers/^(?P<pk>[0-9]+)/edit/?$',
        HeaderUpdateView.as_view(),
        name='header_update'
    ),
    url(
        r'headers/^(?P<pk>[0-9]+)/delete/?$',
        HeaderDeleteView.as_view(),
        name='header_delete'
    ),
]
