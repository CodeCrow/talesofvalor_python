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
PAYPAL_CLIENT_ID = "AdSDoBdlwwChtQlFIskDa4pDPelc8pkwYxwaOf_raUyq9ksXJblsgiUiwjbE0KzTftwp78OogAQbOHaj"
PAYPAL_CLIENT_SECRET = "EIQPfieoZba7Z9RtX7QzkjDn6_6dTEwL_XDs57WgtWAt8TlGo-kV_6j4Y4zE-3LUU8_smxxWZGz6wu5a"
