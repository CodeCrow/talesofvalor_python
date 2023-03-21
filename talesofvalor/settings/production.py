from .common import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG
FILER_DEBUG = DEBUG

ALLOWED_HOSTS = [
    'rhiven.talesofvalor.com',
]

DATABASES = {
    'default': {
        'ENGINE': 'mysql.connector.django',
        'NAME': 'talesof_rhiven',
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
MEDIA_ROOT = BASE_DIR + '/public/media/'

# Paypal integration.  This is the live account
PAYPAL_CLIENT_ID = "AQah38pnBKTKUrULYNTc-XyA6C5UxDQk4m9DiAihBZ3H3o_Uey2TbQaGAMw_zLi5SWJQxheJ_nmCKZWN"
PAYPAL_CLIENT_SECRET = "EDSa1OH9G7mGo2wlC7LFpEvTpBqlJ2RtHFq_Mv4HReD5f4_ps0H2u3eIzrDQ7WtyAwOEK-jU75Zt3eT5"

# Paypal integration for test Tales of Valor account
PAYPAL_CLIENT_ID = "AQcJGiNp_J8n2KU7hVoD8g4O52zT0x0zhMF_TLaooJjJsnexdUkDaHC8DtqE3vYtYfSqPKLZeJjUcItf"
PAYPAL_CLIENT_SECRET = "EE_iU3H-8gfhyCfZcgTySn2aH1g0_PrcwdUN4TJd8IKh_xiBobv1brZpF5DbmyEp7dMYURNAtMe-o4mh"
