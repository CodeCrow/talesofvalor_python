"""
https://www.merixstudio.com/blog/django-fabric/
https://www.obeythetestinggoat.com/book/chapter_automate_deployment_with_fabric.html
https://medium.com/gopyjs/automate-deployment-with-fabric-python-fad992e68b5
"""


import datetime
import importlib
import logging
import os
import re
import stat
import tempfile
from distutils.util import strtobool


from fabric import Connection, task

# from django.conf import settings


try:
    local_settings = importlib.import_module(os.environ['DJANGO_SETTINGS_MODULE'])
except:
    from talesofvalor.settings import local as local_settings

local_db = local_settings.DATABASES

from talesofvalor.settings.stage import DATABASES as stage_db
from talesofvalor.settings.production import DATABASES as prod_db

# Where the remote database connection details come from.  These are the
# settings the site itself runs on, so there is only one place for the name
# and credentials to be wrong.  fabric.yml used to carry a db_name of its
# own and had drifted out of step with both environments.
REMOTE_DATABASES = {
    'stage': stage_db,
    'production': prod_db,
}

LOCAL_DUMPDATA_FOLDER = '../dumpdata'

LOCAL_PROJECT_DIR = os.path.abspath(
    os.path.dirname(__file__)
)

# the settings used for management commands against the local copy.  the
# remote environments carry their own settings module in fabric.yml, and
# that must never be used to point a local command at a live database.
LOCAL_SETTINGS_MODULE = 'talesofvalor.settings.local'

# A dump taken from a newer MySQL carries character sets and collations an
# older local server doesn't recognise, and it fails part way through the
# import leaving a half built database.  Rewrite them on the way in.
#
# - utf8mb4_0900_ai_ci is the MySQL 8.0 default collation and does not exist
#   before 8.0 at all ("ERROR 1273 (HY000): Unknown collation").
# - utf8mb3 is what 8.0.29 and later call the old three byte utf8, including
#   in the _utf8mb3'...' introducers it writes into column defaults.
#
# Ordered longest first so a replacement can't eat part of a later match.
DUMP_SUBSTITUTIONS = (
    ('utf8mb4_0900_ai_ci', 'utf8mb4_unicode_ci'),
    ('utf8mb3', 'utf8'),
)

# Expression defaults, which mysqldump writes as DEFAULT (_utf8mb3''), are
# MySQL 8.0 only.  Before 8.0.13 the DEFAULT (...) form can't be parsed at
# all, and every column that gets one here is a longtext, which an older
# server won't take a plain literal default on either.  So the default has
# to come off rather than be rewritten.  Nothing is lost: Django fills these
# in when it inserts and never leans on a database level default.
DUMP_PATTERNS = (
    (
        "expression default",
        re.compile(r"\s+DEFAULT\s+\(_utf8[a-z0-9]*'(?:[^'\\]|\\.|'')*'\)"),
        ""
    ),
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
        with c.prefix(
            'source ~/.bash_profile && cd {}'.format(
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
                # c.run('echo Updating pip')
                # c.run('pip install --upgrade pip')
                c.run('echo Updating requirements...')
                c.run('pipenv install')

            if migrate is True:
                c.run('echo Migrating database schema...')
                c.run(
                    'pipenv run python manage.py migrate --settings={settings_module}'
                    .format(
                        settings_module=env.
                        settings_module_for_management_commands
                    )
                )

            c.run('echo Updating static files...')
            c.run(
                'pipenv run python manage.py collectstatic --ignore=node_modules '
                '--ignore=sass --ignore=hacks --noinput '
                '--settings={settings_module}'.format(
                    settings_module=env.settings_module_for_management_commands
                )
            )
            c.run('echo Refreshing application...')
            c.run(env.refresh_app_command)


def _dump_remote_db(c, environment):
    """
    Dumps a remote MySQL database.

    The database name and credentials come from that environment's Django
    settings rather than from fabric.yml, so they can't drift apart from
    what the site is actually running against.
    """
    env = c.config
    db = REMOTE_DATABASES[environment]['default']
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%Hh%Mm%Ss")
    dump_filename_base = "{project_name}-{file_key}-{timestamp}.sql"
    file_key = env.verbose_name
    dump_dir = env.db_dump_dir
    database_name = db['NAME']
    file_key = "{}-full".format(file_key)

    dump_filename = dump_filename_base.format(
        project_name=env.project_name,
        file_key=file_key,
        timestamp=timestamp
    )

    backup_location = os.path.join(
        dump_dir, dump_filename
    )
    remote_defaults_file = '/tmp/tov-mysqldump-{}.cnf'.format(timestamp)

    # the options file keeps the password out of the process list, where
    # anyone else with an account on the box could read it.
    options = ['[client]', 'user={}'.format(db['USER'])]
    if db.get('PASSWORD'):
        options.append('password={}'.format(db['PASSWORD']))
    if db.get('HOST'):
        options.append('host={}'.format(db['HOST']))
    if db.get('PORT'):
        options.append('port={}'.format(db['PORT']))

    with Connection(env.hosts, user=env.user, config=c.config) as c:

        c.run(
            'echo Dumping {} database...'.format(env.verbose_name)
        )
        # the dump directory isn't checked in, so it may not be there yet.
        c.run('mkdir -p {}'.format(dump_dir))
        # quoted heredoc, so nothing in the password gets expanded by the
        # shell on the way into the file.
        c.run(
            "umask 077 && cat > {path} <<'TOVCNF'\n{body}\nTOVCNF".format(
                path=remote_defaults_file,
                body='\n'.join(options)
            )
        )
        try:
            # --single-transaction takes the dump inside one transaction
            # rather than locking the tables, so dumping production doesn't
            # hold up the live site.  --quick streams rows out instead of
            # collecting a whole table in memory first.
            # --no-tablespaces because the application's database user has
            # no PROCESS privilege, and without it mysqldump complains about
            # not being able to dump tablespaces.
            c.run(
                'mysqldump --defaults-extra-file={defaults_file} '
                '--single-transaction --quick --no-tablespaces '
                '{database_name} > {backup_location}'.format(
                    defaults_file=remote_defaults_file,
                    database_name=database_name,
                    backup_location=backup_location
                )
            )
        finally:
            c.run('rm -f {}'.format(remote_defaults_file))
    return backup_location


def _sanitize_dumpfile(location):
    """
    Rewrite a dump so an older local MySQL will accept it.

    Works a line at a time so a large dump doesn't have to be held in
    memory, and writes a new file alongside the original rather than editing
    it in place, so the untouched download is still around to look at if an
    import goes wrong.

    Returns the path of the rewritten file and a count of what changed.
    """
    base, extension = os.path.splitext(location)
    cleaned_location = '{}-local{}'.format(base, extension or '.sql')
    counts = {old: 0 for old, _ in DUMP_SUBSTITUTIONS}
    counts.update({label: 0 for label, _, _ in DUMP_PATTERNS})

    # surrogateescape so any bytes that aren't valid utf-8, inside a blob
    # for instance, survive the round trip untouched.
    with open(location, 'r', encoding='utf-8', errors='surrogateescape') as source,\
            open(cleaned_location, 'w', encoding='utf-8', errors='surrogateescape') as target:
        for line in source:
            for label, pattern, replacement in DUMP_PATTERNS:
                line, changed = pattern.subn(replacement, line)
                counts[label] += changed
            for old, new in DUMP_SUBSTITUTIONS:
                if old in line:
                    counts[old] += line.count(old)
                    line = line.replace(old, new)
            target.write(line)

    return cleaned_location, counts


def _local_mysql_defaults_file():
    """
    Write the local database credentials out to a temporary options file.

    Passing a password as a command line argument puts it in the process
    list for anyone on the machine to read, and makes mysql warn about it
    every time.  The caller is responsible for deleting the file.
    """
    db = local_db['default']
    lines = ['[client]']
    for key, setting in (
        ('user', 'USER'),
        ('password', 'PASSWORD'),
        ('host', 'HOST'),
        ('port', 'PORT'),
    ):
        value = db.get(setting, '')
        if value:
            lines.append('{}={}'.format(key, value))

    handle, path = tempfile.mkstemp(prefix='tov-mysql-', suffix='.cnf')
    with os.fdopen(handle, 'w') as options_file:
        options_file.write('\n'.join(lines) + '\n')
    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
    return path


def _ingest_db(c, location):
    """
    Replace the local database with the contents of a dumpfile.

    The database is dropped and rebuilt rather than loaded over the top of
    itself, so tables that no longer exist upstream don't survive as local
    leftovers.
    """
    db_name = local_db['default'].get('NAME')
    defaults_file = _local_mysql_defaults_file()
    try:
        c.run('echo Rebuilding the {} database...'.format(db_name))
        c.run(
            'mysql --defaults-extra-file={defaults_file} '
            '-e "DROP DATABASE IF EXISTS \\`{db_name}\\`; '
            'CREATE DATABASE \\`{db_name}\\` '
            'CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"'.format(
                defaults_file=defaults_file,
                db_name=db_name
            )
        )
        c.run(
            'echo Ingesting {location} into {db_name} database, '
            'this takes a while...'.format(
                location=location,
                db_name=db_name
            )
        )
        c.run(
            'mysql --defaults-extra-file={defaults_file} {db_name} '
            '< {location}'.format(
                defaults_file=defaults_file,
                db_name=db_name,
                location=location
            )
        )
    finally:
        os.remove(defaults_file)

    c.run(
        'echo Successfully ingested {location} into {db_name} '
        'database!'.format(location=location, db_name=db_name)
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
def sync_database(
    c,
    environment,
    ingest=True,
    migrate=True,
    keepdump=False,
    noinput=False
):
    """
    Replace the local database with a copy of a remote one.

    Dumps the database on `environment` (stage or production), brings it
    down, rewrites the character sets and collations the local MySQL is too
    old to understand, drops and rebuilds the local database from it, and
    migrates so the schema matches the branch being worked on.

    The local database is whatever settings.local points at, so the copy and
    the migrate always land on the same place.

    `ingest`:   whether the dump should be loaded, or only downloaded
    `migrate`:  whether to migrate after loading
    `keepdump`: keep the downloaded .sql files instead of cleaning them up
    `noinput`:  skip the confirmation, for unattended runs

    fab sync-database --environment production
    fab sync-database --environment stage --no-migrate
    """
    ingest = _prep_bool_arg(ingest)
    migrate = _prep_bool_arg(migrate)
    keep_dump = _prep_bool_arg(keepdump)
    noinput = _prep_bool_arg(noinput)

    db_name = local_db['default'].get('NAME')
    if ingest and not db_name:
        raise ValueError(
            "No local database name is configured in {}.".format(
                LOCAL_SETTINGS_MODULE
            )
        )

    env = c.config[environment]
    c.config.load_overrides(env)

    if ingest is True and noinput is False:
        # dropping a database can't be undone, so say plainly what is about
        # to happen before doing it.
        print(
            "\nThis will DROP the local database '{db_name}' and rebuild it "
            "from {environment}.\nAnything in it now will be gone.".format(
                db_name=db_name,
                environment=environment
            )
        )
        if input("Type the database name to continue: ").strip() != db_name:
            print("That didn't match, so nothing has been changed.")
            return

    os.makedirs(LOCAL_DUMPDATA_FOLDER, exist_ok=True)

    remote_location = _dump_remote_db(c, environment)
    local_dumpfile_location = _retrieve_db_dumpfile(c, remote_location)

    if ingest is not True:
        c.run(
            'echo Downloaded {}, not ingesting.'.format(
                local_dumpfile_location
            )
        )
        return

    c.run('echo Rewriting the dump for the local database server...')
    cleaned_location, counts = _sanitize_dumpfile(local_dumpfile_location)
    for old, count in counts.items():
        if count:
            c.run(
                'echo "  replaced {} occurrence(s) of {}"'.format(count, old)
            )

    _ingest_db(c, cleaned_location)

    if migrate is True:
        c.run('echo Migrating the local database...')
        c.run(
            'pipenv run python manage.py migrate --settings={settings_module}'
            .format(settings_module=LOCAL_SETTINGS_MODULE)
        )

    if keep_dump is True:
        c.run('echo Dumps kept in {}'.format(LOCAL_DUMPDATA_FOLDER))
    else:
        for path in (local_dumpfile_location, cleaned_location):
            if os.path.exists(path):
                os.remove(path)

    c.run(
        'echo Local database {} now holds a copy of {}.'.format(
            db_name, environment
        )
    )

@task
def sync_media(c, environment, delete=False):
    """
    Downloads user-uploaded media from a server to the
    local settings.MEDIA_ROOT

    `delete`: also remove local files that are no longer on the server, so
              the two match exactly.  Off by default, so a stray local file
              isn't thrown away by surprise.
    """
    delete = _prep_bool_arg(delete)
    env = c.config[environment]
    media_root = local_settings.MEDIA_ROOT.rstrip('/')
    # rsync won't create a missing destination's parents for us.
    os.makedirs(media_root, exist_ok=True)
    c.run(
        'echo Getting media files from {} into {}...'.format(
            env.verbose_name, media_root
        )
    )
    c.run(
        'rsync -avz {delete}--rsh="ssh" {remote_user}@{remote_host}:'
        '{remote_folder}/ {media_root}/'.format(
            delete='--delete ' if delete else '',
            remote_user=env.user,
            remote_host=env.hosts,
            remote_folder=env.media_path.rstrip('/'),
            media_root=media_root
        )
    )

@task
def sync_all(c, environment, ingest_db=True, migrate=True, noinput=False):
    """
    Downloads all user-uploaded media and installs a database dump from
    a remote server
    """
    sync_database(
        c,
        environment,
        ingest=ingest_db,
        migrate=migrate,
        noinput=noinput
    )
    sync_media(c, environment)
