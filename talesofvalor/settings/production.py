from .common import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG
FILER_DEBUG = DEBUG

ALLOWED_HOSTS = [
    'rhiven.talesofvalor.com',
    'rhiven.static.talesofvalor.com',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'talesof_rhiven',
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
MEDIA_ROOT = BASE_DIR + '/public/media/'
STATIC_URL = 'https://rhiven.static.talesofvalor.com/'

# Paypal integration.  This is the live account
PAYPAL_CLIENT_ID = "AQah38pnBKTKUrULYNTc-XyA6C5UxDQk4m9DiAihBZ3H3o_Uey2TbQaGAMw_zLi5SWJQxheJ_nmCKZWN"
PAYPAL_CLIENT_SECRET = "EDSa1OH9G7mGo2wlC7LFpEvTpBqlJ2RtHFq_Mv4HReD5f4_ps0H2u3eIzrDQ7WtyAwOEK-jU75Zt3eT5"

# Recaptcha key
RECAPTCHA_PUBLIC_KEY = '6LdUx0QqAAAAAHovjL_yv358LCCW3RXAgu1_ESNx'
RECAPTCHA_PRIVATE_KEY = '6LdUx0QqAAAAADbFpf5LGB28z-t1FkJ1aIZ3IQLj'
