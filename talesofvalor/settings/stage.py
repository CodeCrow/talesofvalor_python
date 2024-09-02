from .common import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG
FILER_DEBUG = DEBUG

ALLOWED_HOSTS = [
    'rhiven.stage.talesofvalor.com',
    'rhiven.stage.static.talesofvalor.com',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'talesof_rhiven_stage',
        'USER': 'fodder',
        'PASSWORD': 'wereunicorn',
        'HOST': 'mysql.talesofvalor.com',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        },
    }
}

FILE_UPLOAD_TEMP_DIR = os.path.join(BASE_DIR, "tmp")
STATIC_ROOT = BASE_DIR + '/public/static/'
STATIC_URL = 'https://rhiven.stage.static.talesofvalor.com/'

# Paypal integration for test Tales of Valor account
PAYPAL_CLIENT_ID = "AQcJGiNp_J8n2KU7hVoD8g4O52zT0x0zhMF_TLaooJjJsnexdUkDaHC8DtqE3vYtYfSqPKLZeJjUcItf"
PAYPAL_CLIENT_SECRET = "EE_iU3H-8gfhyCfZcgTySn2aH1g0_PrcwdUN4TJd8IKh_xiBobv1brZpF5DbmyEp7dMYURNAtMe-o4mh"
