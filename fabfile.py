"""
https://www.merixstudio.com/blog/django-fabric/
https://www.obeythetestinggoat.com/book/chapter_automate_deployment_with_fabric.html
https://medium.com/gopyjs/automate-deployment-with-fabric-python-fad992e68b5
"""


import datetime
import importlib
import logging
import os
from distutils.util import strtobool


from fabric import Connection, task

# from django.conf import settings


try:
    local_db = importlib.import_module(os.environ['DJANGO_SETTINGS_MODULE']).DATABASES
except:
    from talesofvalor.settings.local import DATABASES as local_db

from talesofvalor.settings.stage import DATABASES as stage_db
from talesofvalor.settings.production import DATABASES as prod_db

LOCAL_DUMPDATA_FOLDER = '../dumpdata'

LOCAL_PROJECT_DIR = os.path.abspath(
    os.path.dirname(__file__)
)


class Environment(object):
    verbose_name = 'default'

env = Environment()

env.project_name = 'talesofvalor'
env.mysql_defaults_file = '~/.my.cnf'


FORMAT = "%(name)s %(funcName)s:%(lineno)d %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)


def _prep_bool_arg(arg):
    """
    Convert a string representation of truth to a Python bool (True/False).

    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    return bool(strtobool(str(arg)))


def _get_settings_file():
    try:
        return os.environ['DJANGO_SETTINGS_MODULE']
    except KeyError:
        return env.settings_module_for_management_commands


@task
def deploy(c, environment, branch=None, migrate=False, updaterequirements=False):
    """
    Deploys the mp_bookpod application to an environment as dictated
    by an environment setup function (like `staging`)
    """

    migrate = _prep_bool_arg(migrate)
    update_requirements = _prep_bool_arg(updaterequirements)
    env = c.config[environment]
    with Connection(env.hosts, user=env.user, config=c.config) as c:
        c.run('ls')
        with c.prefix(
            'source {}/bin/activate && cd {}'.format(
                env.virtualenv_path,
                env.project_dir
            )
        ):
            if branch is None:
                branch = env.default_project_branch
            c.run(
                'echo Pulling talesofvalor on {}...'.format(
                    env.verbose_name
                )
            )
            c.run('git pull')
            c.run(
                'echo Checking out {} branch...'.format(
                    branch
                )
            )
            c.run('git checkout {}'.format(branch))

            c.run('echo updaterequirements:{updaterequirements}'.format(updaterequirements=update_requirements))

            if updaterequirements is True:
                c.run('echo Updating pip')
                c.run('pip install --upgrade pip')
                c.run('echo Updating requirements...')
                c.run('pip install -r requirements.txt')

            if migrate is True:
                c.run('echo Migrating database schema...')
                c.run(
                    'python manage.py migrate --settings={settings_module}'
                    .format(
                        settings_module=env.
                        settings_module_for_management_commands
                    )
                )

            c.run('echo Updating static files...')
            c.run(
                'python manage.py collectstatic --ignore=node_modules '
                '--ignore=sass --ignore=hacks --noinput '
                '--settings={settings_module}'.format(
                    settings_module=env.settings_module_for_management_commands
                )
            )
            c.run('echo Refreshing application...')
            c.run(env.refresh_app_command)


def _dump_remote_db(c):
    """
    Dumps a remote MySQL database
    """
    env = c.config
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%Hh%Mm%Ss")
    dump_filename_base = "{project_name}-{file_key}-{timestamp}.sql"
    file_key = env.verbose_name
    dump_dir = env.db_dump_dir
    database_name = env.db_name
    file_key = "{}-full".format(file_key)

    dump_filename = dump_filename_base.format(
        project_name=env.project_name,
        file_key=file_key,
        timestamp=timestamp
    )

    backup_location = os.path.join(
        dump_dir, dump_filename
    )

    with Connection(env.hosts, user=env.user, config=c.config) as c:

        c.run(
            'echo Dumping {} database...'.format(env.verbose_name)
        )
        c.run(
            'mysqldump --defaults-file={defaults_file} '
            '{database_name} > {backup_location}'.format(
                defaults_file=env.mysql_defaults_file,
                database_name=database_name,
                backup_location=backup_location
            )
        )
    return backup_location


def _ingest_db(c, location):
    """
    Ingests a MySQL database from a dumpfile
    """
    db_name = local_db['default'].get('NAME')
    user = local_db['default'].get('USER', '')
    if user:
        user = '-u {}'.format(user)

    password = local_db['default'].get('PASSWORD', '')
    if password:
        password = ' -p{}'.format(password)

    cmd_kwargs = {
        'db_name': db_name,
        'user': user,
        'location': location,
        'password': password
    }

    with hide('running'):
        local(
            (
                'echo Ingesting {location} into '
                '{db_name} database...'
            ).format(
                **cmd_kwargs
            )
        )
        local(
            'mysql {user}{password} {db_name} < {location}'.format(
                **cmd_kwargs
            )
        )
        local(
            (
                'echo Successfully ingested {location} '
                'into {db_name} database!'
            ).format(
                **cmd_kwargs
            )
        )


def _retrieve_db_dumpfile(c, location):
    """
    Retrieves a .sql file on a remote server (at `location`)
    into LOCAL_DUMPDATA_FOLDER.

    If `ingest_on_success` is True, this file will be ingested
    into your local database (as specified in roadshow_api.settings.local)

    Requires that a env setup function (like `demo_server`) be run prior e.g.:
    $ fab demo_server retrieve_database_dump
    """
    env = c.config
    with Connection(env.hosts, user=env.user, config=c.config) as c:
        c.run(
            'echo Retrieving {} into {}...'.format(
                location,
                LOCAL_DUMPDATA_FOLDER
            )
        )
        path, filename = os.path.split(location)
        destination = os.path.join(
            LOCAL_DUMPDATA_FOLDER,
            filename
        )
        c.get(location, destination)
        return destination

@task
def sync_database(c, environment, ingest=True):
    """
    Dumps out a remote database (as specified by an environment setup
    function like `demo_server`) and ingests it into the local database.

    `ingest`: Signifies whether or not the database dump should be
              immediately ingested
    """
    ingest = _prep_bool_arg(ingest)
    env = c.config[environment]
    c.config.load_overrides(env)
    settings.configure()
    current_settings = _get_settings_file()
    remote_location = _dump_remote_db(c)
    local_dumpfile_location = _retrieve_db_dumpfile(c, remote_location)

    if ingest is True:
       pass #  _ingest_db(env, local_dumpfile_location)

@task
def sync_media(c, environment):
    """
    Downloads user-uploaded media from a server to the
    local settings.MEDIA_ROOT
    """
    env = c.config[environment]
    settings.configure()
    current_settings = _get_settings_file()
    c.run(
        'echo Getting media files from {}...'.format(env.verbose_name)
    )
    c.run(
        'rsync -avz --rsh="ssh" {remote_user}@{remote_host}:'
        '{remote_folder}/ {media_root}/'.format(
            remote_user=env.user,
            remote_host=env.hosts,
            remote_folder=env.media_path.rstrip('/'),
            media_root=settings.MEDIA_ROOT.rstrip('/')
        )
    )

@task
def sync_all(c, environment, ingest_db=True):
    """
    Downloads all user-uploaded media and installs a database dump from
    a remote server
    """
    sync_database(c, environment, ingest=ingest_db)
    sync_media(c, environment)
