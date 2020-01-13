from .common import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG
FILER_DEBUG = DEBUG

ALLOWED_HOSTS = [
    'rhiven.talesofvalor.com',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'talesof_rhiven',
        'USER': 'fodder',
        'PASSWORD': 'wereunicorn',
        'HOST': 'mysql.talesofvalor.com',
        'OPTIONS': {
            'init_command': 'SET innodb_strict_mode=1',
        },
    }
}

FILE_UPLOAD_TEMP_DIR = os.path.join(BASE_DIR, "tmp_upload")
STATIC_ROOT = BASE_DIR + '/public/static/'
