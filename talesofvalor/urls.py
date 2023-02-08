"""
Overarching routing for the application.

The routers for each of the sub-application (players, characters, etc) should
be included as a separate file.
"""

# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.conf import settings
from django.conf.urls import include
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path

from cms.sitemaps import CMSSitemap

admin.autodiscover()

urlpatterns = [
    path('sitemap.xml', sitemap,
         {'sitemaps': {'cmspages': CMSSitemap}},
         name='django.contrib.sitemaps.views.sitemap'),
]


urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),  # NOQA
    path('hijack/', include('hijack.urls')),
    path('', include('django.contrib.auth.urls')),
    # For tags
    path('taggit_autosuggest/', include('taggit_autosuggest.urls')),
    # main application
    path(  # router for the player application.
        'players/',
        include(
            'talesofvalor.players.urls'
        )
    ),
    path(  # router for the event application.
        'events/',
        include(
            'talesofvalor.events.urls'
        )
    ),
    path(  # router for the reports application.
        'reports/',
        include(
            'talesofvalor.reports.urls'
        )
    ),
    path(  # router for the event application.
        'registration/',
        include(
            'talesofvalor.registration.urls'
        )
    ),
    path(  # router for the between game skills application.
        'attendance/',
        include(
            'talesofvalor.attendance.urls'
        )
    ),
    path(  # router for the character application.
        'characters/',
        include(
            'talesofvalor.characters.urls'
        )
    ),
    path(  # router for the origins application.
        'origins/',
        include(
            'talesofvalor.origins.urls'
        )
    ),
    path(  # router for the skills application.
        'skills/',
        include(
            'talesofvalor.skills.urls'
        )
    ),
    path(  # router for the between game skills application.
        'betweengameskills/',
        include(
            'talesofvalor.betweengameskills.urls'
        )
    ),
    path(  # router for the rules application.
        'rules/',
        include(
            'talesofvalor.rules.urls'
        )
    ),
    # for paypal
    path('paypal/', include('paypal.standard.ipn.urls')),
    path('notifications/', include('django_nyt.urls')),
    path('wiki/', include('wiki.urls')),
    # for the main cms
    path('', include('cms.urls'))

)

# This is only needed when using runserver.
if settings.DEBUG:
    urlpatterns += \
        static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)\
        + staticfiles_urlpatterns()
