from .common import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG
FILER_DEBUG = DEBUG

ALLOWED_HOSTS = [
    'rhiven.stage.talesofvalor.com',
]

DATABASES = {
    'default': {
        'ENGINE': 'mysql.connector.django',
        'NAME': 'talesof_rhiven_stage',
        'USER': 'fodder',
        'PASSWORD': 'wereunicorn',
        'HOST': 'mysql.talesofvalor.com',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES',innodb_strict_mode=1",
            'use_pure': True
        },
    }
}

FILE_UPLOAD_TEMP_DIR = os.path.join(BASE_DIR, "tmp_upload")
STATIC_ROOT = BASE_DIR + '/public/static/'
