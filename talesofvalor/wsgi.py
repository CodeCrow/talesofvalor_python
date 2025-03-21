"""
WSGI config for talesofvalor project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os
import sys
from django.core.wsgi import get_wsgi_application

# Add the project directory to the sys.path
sys.path.append('/home/talesof/rhiven.talesofvalor.com')


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "talesofvalor.settings")

application = get_wsgi_application()
