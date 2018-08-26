"""
Overarching routing for the application.

The routers for each of the sub-application (players, characters, etc) should
be included as a separate file.
"""

# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.static import serve

from cms.sitemaps import CMSSitemap

admin.autodiscover()

urlpatterns = [
    url(r'^sitemap\.xml$', sitemap,
        {'sitemaps': {'cmspages': CMSSitemap}}),
]

urlpatterns += i18n_patterns(
    url(r'^admin/', include(admin.site.urls)),  # NOQA
    url(r'^', include('django.contrib.auth.urls')),
    url(r'^taggit_autosuggest/', include('taggit_autosuggest.urls')), # For tags
    # for the wiki
    url(r'^notifications/', include('django_nyt.urls')),
    url(r'^wiki/', include('wiki.urls')),
    # main application
    url(  # router for the player application.
        r'^players/',
        include(
            'talesofvalor.players.urls',
            namespace="players",
            app_name="talesofvalor"
        )
    ),
    url(  # router for the event application.
        r'^events/',
        include(
            'talesofvalor.events.urls',
            namespace="events",
            app_name="talesofvalor"
        )
    ),
    url(  # router for the character application.
        r'^characters/',
        include(
            'talesofvalor.characters.urls',
            namespace="characters",
            app_name="talesofvalor"
        )
    ),
    url(  # router for the origins application.
        r'^origins/',
        include(
            'talesofvalor.origins.urls',
            namespace="origins",
            app_name="talesofvalor"
        )
    ),
    url(  # router for the skills application.
        r'^skills/',
        include(
            'talesofvalor.skills.urls',
            namespace="skills",
            app_name="talesofvalor"
        )
    ),
    url(r'^', include('cms.urls')),
)

# This is only needed when using runserver.
if settings.DEBUG:
    urlpatterns = [
        url(r'^media/(?P<path>.*)$', serve,
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    ] + staticfiles_urlpatterns() + urlpatterns
