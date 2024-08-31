import os
gettext = lambda s: s
DATA_DIR = os.path.dirname(os.path.dirname(__file__))
"""
Django settings for talesofvalor project.

Generated by 'django-admin startproject' using Django 1.8.17.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '-a=ywh5ngvis#gf195lq&j6cd$8j0)i&gb=s&&a6_8eh@mx%)5'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

"""
ALLOWED_HOSTS = [
    'rhiven.talesofvalor.com',
    'rhiven.static.talesofvalor.com',
    # Add any additional domains as needed
]
"""

CSRF_TRUSTED_ORIGINS = [
    'https://rhiven.talesofvalor.com',
    'https://rhiven.static.talesofvalor.com',

]

# Application definition
WSGI_APPLICATION = 'talesofvalor.wsgi.application'

ROOT_URLCONF = 'talesofvalor.urls'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Who to send problems to
ADMINS = [
    ('Rob Archer', 'rob@crowbringsdaylight.com'),
]
# default error emails
SERVER_EMAIL = 'webmaster@talesofvalor.com'
# default email sender for production.  This email address must exist.
DEFAULT_FROM_EMAIL = 'characterupdate@talesofvalor.com'
# general staff email
STAFF_EMAIL = 'Tov3staff@googlegroups.com'
# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases


DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static_global'),
)

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
FILE_UPLOAD_PERMISSIONS = 0o644

SITE_ID = 1

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'players:player_redirect_detail'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'talesofvalor', 'templates'),
        ],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'sekizai.context_processors.sekizai',
                'cms.context_processors.cms_settings',
                'talesofvalor.context_processors.character_settings'
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader'
            ],
        },
    },
]


MIDDLEWARE = (
    'cms.middleware.utils.ApphookReloadMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'hijack.middleware.HijackUserMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'cms.middleware.language.LanguageCookieMiddleware'
)

INSTALLED_APPS = (
    'djangocms_admin_style',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.staticfiles',
    'django.contrib.messages',
    'cms',
    'menus',
    'sekizai',
    'treebeard',
    'djangocms_text_ckeditor',
    'filer',
    'easy_thumbnails',
    'djangocms_file',
    'djangocms_picture',
    'djangocms_link',
    'djangocms_style',
    'djangocms_snippet',
    'djangocms_video',
    # impersonating users
    'hijack',
    # The wiki
    'django.contrib.humanize.apps.HumanizeConfig',
    'django_nyt.apps.DjangoNytConfig',
    'mptt',
    'sorl.thumbnail',
    'wiki.apps.WikiConfig',
    'wiki.plugins.attachments.apps.AttachmentsConfig',
    'wiki.plugins.notifications.apps.NotificationsConfig',
    'wiki.plugins.images.apps.ImagesConfig',
    'wiki.plugins.macros.apps.MacrosConfig',
    # for api/ajax calls
    'rest_framework',
    # For tagging
    'taggit',
    # for autosuggest
    'dal',
    'dal_select2',
    # for autosuggest OF tagging
    'dal_select2_taggit',
    # Main ToV code
    'talesofvalor',
    'talesofvalor.services',
    'talesofvalor.players',
    'talesofvalor.skills',
    'talesofvalor.origins',
    'talesofvalor.events',
    'talesofvalor.characters',
    'talesofvalor.betweengameabilities',
    'talesofvalor.attendance',
    'talesofvalor.charactermessages',
    'talesofvalor.comments',
    'talesofvalor.rules',
    'talesofvalor.registration',
    'talesofvalor.reports',
    # Django admin
    'django.contrib.admin',
    'hijack.contrib.admin',
)

LANGUAGES = (
    ## Customize this
    ('en', gettext('en')),
)

CMS_LANGUAGES = {
    ## Customize this
    'default': {
        'public': True,
        'hide_untranslated': False,
        'redirect_on_fallback': True,
    },
    1: [
        {
            'public': True,
            'code': 'en',
            'hide_untranslated': False,
            'name': gettext('en'),
            'redirect_on_fallback': True,
        },
    ],
}

CMS_TEMPLATES = (
    ## Customize this
    ('fullwidth.html', 'Fullwidth'),
    ('sidebar_left.html', 'Sidebar Left'),
    ('sidebar_right.html', 'Sidebar Right')
)

CMS_PERMISSION = True

CMS_PLACEHOLDER_CONF = {}

DATABASES = {
    'default': {
        'CONN_MAX_AGE': 0,
        'ENGINE': 'django.db.backends.sqlite3',
        'HOST': 'localhost',
        'NAME': 'project.db',
        'PASSWORD': '',
        'PORT': '',
        'USER': ''
    }
}

MIGRATION_MODULES = {

}

'''
Taggit settings
'''
# make life easier 
TAGGIT_CASE_INSENSITIVE = True

'''
Paypal secrets
'''
# PAYPAL_CLIENT_ID = os.environ['PAYPAL_CLIENT_ID']
# PAYPAL_CLIENT_SECRET = os.environ['PAYPAL_CLIENT_SECRET']

PAYPAL_CLIENT_ID = "AQcJGiNp_J8n2KU7hVoD8g4O52zT0x0zhMF_TLaooJjJsnexdUkDaHC8DtqE3vYtYfSqPKLZeJjUcItf"
PAYPAL_CLIENT_SECRET = "EE_iU3H-8gfhyCfZcgTySn2aH1g0_PrcwdUN4TJd8IKh_xiBobv1brZpF5DbmyEp7dMYURNAtMe-o4mh"

THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters'
)

'''
RESTFRAMEWORK
'''
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    )
}

'''
Hijacking Permissions
If we need more granular permissions
https://django-hijack.readthedocs.io/en/stable/customization/#hijack-permission
'''
HIJACK_PERMISSION_CHECK = "hijack.permissions.superusers_and_staff"
