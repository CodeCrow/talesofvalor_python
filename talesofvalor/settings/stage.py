from .common import *

ALLOWED_HOSTS = [
    'tov.crowbringsdaylight.com',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'talesofvalor',
        'USER': 'cr0w_us3r',
        'PASSWORD': 't3stc0rvid',
        'HOST': 'mysql.crowbringsdaylight.com'
    }
}

FILE_UPLOAD_TEMP_DIR = os.path.join(BASE_DIR, "tmp_upload")
STATIC_ROOT = BASE_DIR + '/public/static/'

'''
Paypal integration with  django-paypal
'''
PAYPAL_TEST = DEBUG
PAYPAL_RECEIVER_EMAIL = "replaceme@gmail.com"