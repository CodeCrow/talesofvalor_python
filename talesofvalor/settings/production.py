from common import *

FILE_UPLOAD_TEMP_DIR = os.path.join(BASE_DIR, "tmp")

DEBUG = False
TEMPLATE_DEBUG = DEBUG
FILER_DEBUG = DEBUG

ALLOWED_HOSTS = [
    '*.wgbh.org',
    '*.wgbh.org.',
]

ALLOWED_HOSTS = [
    'lsintspl3.wgbh.org',
    'ilp-prod.wgbh.org'
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
        'OPTIONS': {
            'init_command':'SET storage_engine=MYISAM',
            'read_default_file': '/wgbh/il-prod/config/mysql.cnf',
        }
    }
}

# good info: 
# https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/
# http://cheat.readthedocs.io/en/latest/django/logging.html
'''
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/wgbh/logs/il-prod.log',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['file'],
                'level': 'INFO',
                'propagate': True,
            },
            'spl': {
                'handlers': ['file'],
                'level': 'INFO',
                'propagate': True,
            },
        },
    }
'''