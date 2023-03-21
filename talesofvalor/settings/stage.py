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
            'use_pure': True
        },
    }
}

FILE_UPLOAD_TEMP_DIR = os.path.join(BASE_DIR, "tmp_upload")
STATIC_ROOT = BASE_DIR + '/public/static/'

# Paypal integration for test Tales of Valor account
PAYPAL_CLIENT_ID = "AQcJGiNp_J8n2KU7hVoD8g4O52zT0x0zhMF_TLaooJjJsnexdUkDaHC8DtqE3vYtYfSqPKLZeJjUcItf"
PAYPAL_CLIENT_SECRET = "EE_iU3H-8gfhyCfZcgTySn2aH1g0_PrcwdUN4TJd8IKh_xiBobv1brZpF5DbmyEp7dMYURNAtMe-o4mh"
