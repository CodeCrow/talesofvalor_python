import sys, os

cwd = os.getcwd()
sys.path.append(cwd)
sys.path.append(cwd + '/talesofvalor')

INTERP = os.path.expanduser("~/.virtualenvs/talesofvalor/bin/python")

if sys.executable != INTERP: os.execl(INTERP, INTERP, *sys.argv)

sys.path.insert(0,'$HOME/.virtualenvs/talesofvalor/bin')
sys.path.insert(0,'$HOME/.virtualenvs/talesofvalor/lib/python2.7/site-packages/django')
sys.path.insert(0,'$HOME/.virtualenvs/talesofvalor/lib/python2.7/site-packages')

os.environ['DJANGO_SETTINGS_MODULE'] = 'talesofvalor.settings.stage'
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
