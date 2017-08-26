import datetime
import importlib
import os
from distutils.util import strtobool

from django.conf import settings

from fabric.api import env, hide, prefix, run
from fabric.operations import get, local

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

env.project_name = 'talesofvalor'
env.mysql_defaults_file = '~/.my.cnf'
try:
    env.settings_module_for_management_commands = os.environ['DJANGO_SETTINGS_MODULE']
except KeyError:
    env.settings_module_for_management_commands = 'talesofvalor.settings.local'


def _prep_bool_arg(arg):
    """
    Convert a string representation of truth to a Python bool (True/False).

    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    return bool(strtobool(str(arg)))

def stage():
    """
    Sets the environment variables needed for the Masterpiece Book Club
    Podcast publishing box.
    """
    env.verbose_name = 'stage'
    env.forward_agent = True
    env.hosts = ['murderofone@bonanza.dreamhost.com']
    env.db_settings = stage_db['default']
    env.db_dump_dir = '/home/murderofone/tov.crowbringsdaylight.com/dumpdata'
    env.virtualenv_path = (
        '/home/murderofone/.virtualenvs/talesofvalor'
    )
    env.project_dir = (
        '/home/murderofone/tov.crowbringsdaylight.com'
    )
    env.default_project_branch = 'stage'
    env.refresh_app_command = (
        'pkill python'
    ).format(
        env.project_dir
    )
    env.settings_module_for_management_commands = 'talesofvalor.settings.stage'
    env.mysql_defaults_file = '/home/murderofone/tov.talesofvalor.com/config/mysql.cnf'




def production():
    """
    Sets the environment variables needed for the Masterpiece Book Club
    Podcast publishing box.
    """
    env.verbose_name = 'production'
    env.forward_agent = True
    env.hosts = ['wgbh@184.72.241.218']
    env.db_settings = prod_db['default']
    env.db_dump_dir = '/home/wgbh/Masterpiece/dumpdata'
    env.virtualenv_path = (
        '/home/wgbh/__virtualenvs/Stacks-Masterpiece-BookClubPodcast'
    )
    env.project_dir = (
        '/home/wgbh/Masterpiece/Stacks-Masterpiece-BookClubPodcast'
    )
    env.default_project_branch = 'master '
    env.restart_webserver_command = 'sudo service apache2 restart'
    env.refresh_app_command = (
        'touch {0}/mp_bookpod/wsgi/prod.py'
    ).format(
        env.project_dir
    )
    env.settings_module_for_management_commands = 'mp_bookpod.settings.prod'
    env.mysql_defaults_file = '/home/wgbh/Masterpiece/.mysql-mp_bookpod.cnf'
    env.live_publish_rsync_root = (
        '/home/wgbh/Masterpiece/Stacks-Masterpiece-BookClubPodcast/'
        'STATIC_SITE_FILES/wgbh/masterpiece/podcast-book-club'
    )


def deploy(branch=None, migrate=False, update_requirements=False):
    """
    Deploys the mp_bookpod application to an environment as dictated
    by an environment setup function (like `staging`)
    """
    migrate = _prep_bool_arg(migrate)
    update_requirements = _prep_bool_arg(update_requirements)
    with hide('running'):
        with prefix(
            'source {}/bin/activate && cd {}'.format(
                env.virtualenv_path,
                env.project_dir
            )
        ):
            if branch is None:
                branch = env.default_project_branch
            run(
                'echo Pulling mp_bookpod on {}...'.format(
                    env.verbose_name
                )
            )
            run('git pull')
            run(
                'echo Checking out {} branch...'.format(
                    branch
                )
            )
            run('git checkout {}'.format(branch))

            if update_requirements is True:
                run('echo Updating requirements...')
                run('pip install -r requirements.txt')

            if migrate is True:
                run('echo Migrating database schema...')
                run(
                    'python manage.py migrate --settings={settings_module}'
                    .format(
                        settings_module=env.
                        settings_module_for_management_commands
                    )
                )

            run('echo Updating static files...')
            run(
                'python manage.py collectstatic --ignore=node_modules '
                '--ignore=sass --ignore=hacks --noinput '
                '--settings={settings_module}'.format(
                    settings_module=env.settings_module_for_management_commands
                )
            )
            run('echo Refreshing application...')
            run(env.refresh_app_command)


def _dump_remote_db():
    """
    Dumps a remote MySQL database
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%Hh%Mm%Ss")
    dump_filename_base = "{project_name}-{file_key}-{timestamp}.sql"
    file_key = env.verbose_name
    dump_dir = env.db_dump_dir
    command = run
    database_name = env.db_settings.get('NAME')
    file_key = "{}-full".format(file_key)

    dump_filename = dump_filename_base.format(
        project_name=env.project_name,
        file_key=file_key,
        timestamp=timestamp
    )

    backup_location = os.path.join(
        dump_dir, dump_filename
    )

    with hide('running'):
        command(
            'echo Dumping {} database...'.format(env.verbose_name)
        )
        command(
            'mysqldump --defaults-file={defaults_file} '
            '{database_name} > {backup_location}'.format(
                defaults_file=env.mysql_defaults_file,
                database_name=database_name,
                backup_location=backup_location
            )
        )
    return backup_location


def _ingest_db(location):
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


def _retrieve_db_dumpfile(location):
    """
    Retrieves a .sql file on a remote server (at `location`)
    into LOCAL_DUMPDATA_FOLDER.

    If `ingest_on_success` is True, this file will be ingested
    into your local database (as specified in roadshow_api.settings.local)

    Requires that a env setup function (like `demo_server`) be run prior e.g.:
    $ fab demo_server retrieve_database_dump
    """
    with hide('running'):
        local(
            'echo Retrieving {} into {}...'.format(
                location,
                LOCAL_DUMPDATA_FOLDER
            )
        )
        get(location, LOCAL_DUMPDATA_FOLDER)
        path, filename = os.path.split(location)
        return os.path.join(
            LOCAL_DUMPDATA_FOLDER,
            filename
        )


def sync_database(ingest=True):
    """
    Dumps out a remote database (as specified by an environment setup
    function like `demo_server`) and ingests it into the local database.

    `ingest`: Signifies whether or not the database dump should be
              immediately ingested
    """
    ingest = _prep_bool_arg(ingest)

    remote_location = _dump_remote_db()
    local_dumpfile_location = _retrieve_db_dumpfile(remote_location)

    if ingest is True:
        _ingest_db(local_dumpfile_location)


def sync_media():
    """
    Downloads user-uploaded media from a server to the
    local settings.MEDIA_ROOT
    """
    local(
        'echo Getting media files from {}...'.format(env.verbose_name)
    )
    with hide('running'):
        local(
            'rsync -avz --rsh="ssh" {remote_host}:'
            '{remote_folder}/ {media_root}/'.format(
                remote_host=env.host_string,
                remote_folder=env.media_folder.rstrip('/'),
                media_root=settings.MEDIA_ROOT.rstrip('/')
            )
        )


def sync_all(ingest_db=True):
    """
    Downloads all user-uploaded media and installs a database dump from
    a remote server
    """
    sync_database(ingest=ingest_db)
    sync_media()

