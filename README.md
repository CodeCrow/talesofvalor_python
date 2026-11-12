# Useful and reference links
* [Installing MySQL on OS X](https://ruddra.com/install-mysqlclient-macos/) 
* [Django](https://www.djangoproject.com/)
* [Django CMS](https://docs.django-cms.org/en/latest/)

# Installation

## Get the code
Clone Repository 
https://github.com/CodeCrow/talesofvalor_python

```
$ git clone https://github.com/CodeCrow/talesofvalor_python.git
$ cd talesofvalor_python
```

## Get repo write permission
Send your git username to Rob Archer so he can give you write permission to the repo.

## Set up virtual environment and package managment

[Reference](https://pipenv.pypa.io/en/latest/)

[Install pipenv](pip install --user pipenv) (if it isn't installed already)

*Nix/OS X:
```
pip install --user pipenv
```

Windows:
Most of the windows commands are the same except you have to add ```python -m``` to the front of the command for instance to install pipenv use:
```
python -m pip install --user pipenv
```
When the installation is done, open a new shell/terminal window. You should now be able to see the result of this command:
```
pipenv --version
```

## install the packages

This installs libraries and modules that support our specific code:

```
pipenv install
```

## Activate the shell with all the modules installed
```
pipenv shell
```

## Set up the database:


### Create a MySQL database for this project:

First, make sure you have a database named `talesofvalor` with a character set of `utf8`.

```
$ mysql
mysql> create database `talesofvalor` character set utf8;
Query OK, 1 row affected (0.00 sec)
mysql> exit
```

## Add local environment variables
1. Install direnv for your machine: [https://direnv.net/docs/installation.html](https://direnv.net/docs/installation.html)	
2. copy the contents in "envrc_template" into the ".envrc" file in the base directory of the code.

Allow the code to run:

```
$ direnv allow .
```

## Update the settings to run locally:

Copy the "local.py" file and update it with your requirements for accessing the database.

```
cd talesofvalor/settings
cp stage.py local.py
vi local.py
```
You can replace ```vi``` with an editor of your choice.

Change the areas marked with **#########** to values for your database:

```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', 
        'NAME': 'talesofvalor',
        'USER': '############',
        'PASSWORD': '############',
        'HOST': '',                     
        'PORT': '',                      # Set to empty string for default.
        'OPTIONS': {
        }

    }
}


# email back end for development only
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

```

## database and media syncing


Pull down the database and media files from the development server **not needed yet**:

```
$ fab sync_all:dev,yourname -u wgbh
```

Run the initial migrations in case there are differences between the development server database and the code currently in the development repository.

```
$ ./manage.py migrate --settings=talesofvalor.settings.local
```

# Set up the super user
To be able to log in for the first time (or if you forget your logins!) you have to create a "superuser".

```
$ ./manage.py createsuperuser --settings=talesofvalor.settings.local
```

# Run the development server
So you can now develop locally.

Make sure you have your pipenv shell running:
```
pipenv shell
```

Then activate the server:

```
$ ./manage.py runserver --settings=talesofvalor.settings.local
```

Open a browser and go to [http://127.0.0.1:8000/admin/]()

You should now see a login screen!

## email on the development server

So you don't have to set up a local SMTP server, make sure the following is added to your local settings file (local.py).

```
# email back end for development only
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

This will display the emails sent in the server log rather than trying to send emails.


# CSS
The CSS files are created using [SASS](https://sass-lang.com/) using the [gulp workflow](https://gulpjs.com/).

To use gulp, you have to install [node and the node package manager](https://docs.npmjs.com/try-the-latest-stable-version-of-node) if it is not there already:

```
$ brew install node
```

Now, install all the needed packages:

```
$ npm install
```

This will read ```package.json``` file and install the required packages.  

Now you can run ```gulp``` and any changes that you make to the ```SASS``` files will be detected and built into the master css file.  This command will continue running until it is stopped.

```
$ gulp
```

# Deployment:

Deployment uses Fabric 2.0.  If you are used to Fabric < 2, sending CLI variables looks a little different.

`fab deploy --environment {{ environment_name}} [--migrate][--updaterequirements][--branch {{ branch_name }} ]`

Where “environment” is “stage”, “production”, “development”, and “branch_name” is the branch that should be deployed.

Example:
`fab deploy --environment stage --migrate`

This would would deploy the latest default staging branch to the 'stage' environment and run existing migrations.


# Database Info

MySQL now defaults to using INNO DB as the storage engine, which is awesome, except it throws constraints around like candy, which doesn't play well with plugins.  So we sometimes have to remove the constraints.

Example Error: 

``IntegrityError: (1452, 'Cannot add or update a child row: a foreign key constraint fails (`spldjangocms`.`video_splvideoasset`, CONSTRAINT `cmsplugin_ptr_id_refs_id_20f5c1c6` FOREIGN KEY (`cmsplugin_ptr_id`) REFERENCES `cms_cmsplugin` (`id`))')``

To fix the error, you can either remove the constrait using a GUI such as [Sequel Pro](http://www.sequelpro.com/) or the following command:

``ALTER TABLE video_splvideoasset DROP FOREIGN KEY 'cmsplugin_ptr_id';``

# Testing
## Paypal
1. go to paypal.com
2. click "developer"
3. log in with regular account
4. Test users are under "accounts"

# Continuing to work
## Once you have everything working, how do you restart everything when you've been away for a few days
In separate terminal windows, activate the venv and then run:
* ./manage.py runserver --settings=talesofvalor.settings.local
* gulp
and then on github, look at the Projects page to see the todo list:
  https://github.com/CodeCrow/talesofvalor_python/projects
or at the more granular level, the Issues list:
  https://github.com/CodeCrow/talesofvalor_python/issues

If you change a model and need to migrate the changes to the database:
$ ./manage.py makemigrations --settings=talesofvalor.settings.local

Nuking and re-creating the database:
in mysql using a db snapshot:
> drop database talesofvalor
> source path/to/filename
or use migrate to minimally repopulate:
$ ./manage.py migrate --settings=talesofvalor.settings.local

Importing an exported db:
1. Download the exported file
2. Fire up mysql ("mysql" at the prompt)
3. If you want to see what dbs exist:
   show databases;
4. Back at the mysql prompt:
   mysql> create database new_database_name;
5. mysql> use new_database_name
6. mysql> source path/to/export/file
7. Go to the local settings file (typically ROOT/talesofvalor/settings/local.py ) and update the database's NAME

## Get the latest code
1. Navigate to where you have the code.
2. Pull the newest code from the repository:
  3. ```git pull```

## Activate the virtual environment
This loads the correct modules and prepares the code libraries

1.  Navigate to where you have the code.
2.  ```pipenv shell``` 

## Run the gulp compiler for styling and javascript
1. Navigate to where you have the code.
2. Start the compiler:
   3. ```gulp``` 

## Run the development server
1. Navigate to where you have the code.
2. Start the server:
  3. ```./manage.py migrate --settings=talesofvalor.settings.local```

## Update the database after making a change to any of the ```models.py``` files
1. Create the migration files:
  2.  ```./manage.py makemigrations --settings.talesofvalor.local```
3. Run the migration files:
  4.  ```./manage.py migrate --settings.talesofvalor.local```

## Update the database from others' changes
You are basically going to run the last step of updating the database, because other people have already created the migration files.

1. Navigate to where you have the code.
2. Run the migration
  3. ```./manage.py migrate --settings.talesofvalor.local```

## Removing and recreating the database
If something has gone wrong, or you want start from scratch, data-wise, you can recreate the database.

1.  Log into your local mysql server
  2. ```mysql -u username -p```
3. Drop the database:
  4. ```DROP DATABASE databasename;```
5. Exit mysql: 
  6. ```exit;```
7. Create the database again:
  8. ```./manage.py migrate --settings=talesofvalor.settings.local```

Remember, this gets rid of the entire database.  You'll have to recreate your superuser to log in again.  And there is no going back . . .

## Installing new external modules
If you need a module to help with development, you would use pipenv to install it.

1. Make sure you are in the code director
2. Add the module:
	3. 	```pipenv install modulename```
4. commit the changes that it makes to the ```Pipfile``` file.


## Getting the newest database from the production site

If you want to get the database from the production site, so you can look at something or test something with valid data, you can log into the database online and export that.

1. Enter 'mysql.talesofvalor.com' in your browser.
2. Enter the username and password (Contact Rob Archer for that information)
3. Choose 'talesof_rhiven' from the left hand list.
4. Click 'Export' from the top navigation.
5. Format the export as SQL and click the "Go" button.
  6. You can change export method to 'custom' if you want more control.
7. Save the SQL file somewhere on your machine and take note of the location.
8. Open the command line on your machine.
9. Log into your local mysql.
  10. ```mysql -u username -p```
11. Create a new database.
  12. ```create database `talesofvalor_test` character set utf8;```
  13. You can name it whatever you want.
14. Indicate that you want to use that database:
  15. ```use talesofvalor_test;```
13. Load the data into the new database:
  14. ```source path/to/exported/database;```
15. Update the settings file to point to the new database:
  16.  
  
  ```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', 
        'NAME': 'talesofvalor_test',
        'USER': '############',
        'PASSWORD': '############',
        'HOST': '',                     
        'PORT': '',                      # Set to empty string for default.
        'OPTIONS': {
        }
     }
}
```
  17.  make sure the 'NAME' here matches the name of the database you created.
18. Restart the server.


# Testing
## Unit tests

`manage.py` is at the repository root and the apps live inside the
`talesofvalor` package, so test labels need the full dotted path.

Make sure your pipenv shell is running, then:

```
# every test
$ ./manage.py test --settings=talesofvalor.settings.local

# one app
$ ./manage.py test --settings=talesofvalor.settings.local talesofvalor.players

# one module, class or single test
$ ./manage.py test --settings=talesofvalor.settings.local talesofvalor.players.tests.test_models.RequestCompleteTest
```

Add `--noinput` to drop a leftover test database from an interrupted run
instead of being prompted for it.

Tests for an app live in that app's own `tests/` package, for example
`talesofvalor/players/tests/test_models.py`.

Things worth knowing when a test fails for reasons that look unrelated to
your change:

* The test database is built by running every migration from scratch, so a
  migration that only works against an existing database will fail here even
  though it applied fine locally.
* django-cms keeps the logged in user in a threadlocal that outlives a test.
  Call `cms.utils.permissions.set_current_user(None)` in `setUp` before
  creating any users, or they get stamped as created by a user the previous
  test has already rolled back.

# Running on Dreamhost
Instructions for running this on dreamhost and letting it restart.

Allowing the server to run through crashes and reboots: https://help.dreamhost.com/hc/en-us/articles/23971547819412-Using-linger-with-Gunicorn

We want the following information specifically on `/home/talesof/.config/systemd/user`

## default.target.wants
### file: gunicorn.service
```
[Unit]
Description=Gunicorn instance to serve Tales of Valor production application
After=network.target

[Service]
WorkingDirectory=/home/talesof/rhiven.talesofvalor.com
Environment="PATH=/home/talesof/rhiven.talesofvalor.com/.venv/bin"
ExecStart=/home/talesof/rhiven.talesofvalor.com/.venv/bin/gunicorn --workers 3 --bind=rhiven.talesofvalor.com:8000 passen
ger_wsgi:application --access-logfile /home/talesof/logs/rhiven.talesofvalor.com/gunicorn_access --error-logfile /home/ta
lesof/logs/rhiven.talesofvalor.com/gunicorn_error --capture-output
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
# StandardOutput=append:/home/talesof/output.log
# StandardError=append:/home/talesof/error.log

[Install]
WantedBy=default.target
```

## gunicorn.service
```
[Unit]
Description=Gunicorn instance to serve Tales of Valor production application
After=network.target

[Service]
WorkingDirectory=/home/talesof/rhiven.talesofvalor.com
Environment="PATH=/home/talesof/rhiven.talesofvalor.com/.venv/bin"
ExecStart=/home/talesof/rhiven.talesofvalor.com/.venv/bin/gunicorn --workers 3 --bind=rhiven.talesofvalor.com:8000 passen
ger_wsgi:application --access-logfile /home/talesof/logs/rhiven.talesofvalor.com/gunicorn_access --error-logfile /home/ta
lesof/logs/rhiven.talesofvalor.com/gunicorn_error --capture-output
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
# StandardOutput=append:/home/talesof/output.log
# StandardError=append:/home/talesof/error.log

[Install]
WantedBy=default.target
```

## gunicorn.servicetest

This was for testing the service to see what was happening: 

```
[Unit]
Description=Gunicorn instance to serve Tales of Valor production application
After=network.target

[Service]
User=talesof
Group=pg1559836  # Use the existing group of the talesof user
WorkingDirectory=/home/talesof/rhiven.talesofvalor.com
Environment="PATH=/home/talesof/rhiven.talesofvalor.com/.venv/bin"
ExecStart=/home/talesof/rhiven.talesofvalor.com/.venv/bin/gunicorn --workers 3 --bind 0.0.0.0:8000 talesofvalor.wsgi:appl
ication
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
```

## Recovering from upgrades

Often, when there has been an upgrade, we have to reenable linger.   Log in and run the following command:

```
loginctl enable-linger
```

You might have to enable `gunicorn`:

```
systemctl --user enable gunicorn
```

Then start it:

```
systemctl --user start gunicorn
```

And make sure it is running

```
systemctl --user status gunicorn
```

## `fab init`

The steps above are what `fab init` does, so they rarely need doing by hand:

```
$ fab init --environment production
$ fab init --environment stage
```

It enables linger, makes sure the unit and log directories exist, reconciles
`~/.config/systemd/user/gunicorn.service` and `~/logrotate-gunicorn.conf`
against the templates in `fabfile.py`, schedules the weekly log rotation,
enables the service so it returns after a reboot, and starts it if it is not
already running. Then it prints the state of each link in that chain:

```
production gunicorn
  linger      yes
  unit        present, matches
  rotation    present, matches, already scheduled
  python      3.10.1 OpenSSL 3.0.2 15 Mar 2022
  enabled     enabled
  active      active
  responding  302
```

It is safe to run against a healthy server. It will not restart a running
service unless you pass `--restart`, and it will not overwrite a unit or
logrotate config that differs from the template unless you pass
`--writeunit` — the server is treated as the authority until you say
otherwise.

`linger` is the one to look at after a DreamHost upgrade: gunicorn runs as a
systemd *user* service, and without linger it dies when your login session
ends. The site stays up until something restarts, then quietly does not come
back.

If `python` says `BROKEN`, a hand built python in that account is linked
against a library the OS no longer ships. That is what happened to stage: its
python-3.9.2 wanted `libssl.so.1.1`, which the move to Ubuntu 22.04 replaced
with OpenSSL 3, so gunicorn could not even import `ssl`. Rebuilding the
virtualenv on the system python 3.10 fixed it.

## When DreamHost upgrades the OS

This has now broken the site twice, both times in the same shape: something
in the virtualenv is linked against a system library the new OS no longer
ships, so gunicorn starts and its workers die immediately.

| Upgrade | What went | Symptom |
| --- | --- | --- |
| 22.04 | `libssl.so.1.1` | stage's python-3.9.2 could not `import ssl` |
| 26.04 | `libmysqlclient.so.21` | `mysqlclient` fails, every worker dies on import |
| 26.04 | `/usr/bin/python3.10` | `pipenv` fails with `bad interpreter`, so deploys stop |
| 26.04 | `PrivateTmp=true` | systemd 259 refuses the namespace, `status=226/NAMESPACE` |

The 26.04 upgrade took production down for roughly two days before anyone
noticed, because a 503 from the proxy looks the same whatever the cause.

### First thing to run

```
$ fab init --environment production
```

Its report names the usual suspects: `linger` goes off on an upgrade, and
`python` reports `BROKEN` when the interpreter has lost a library. If both
look fine but the site is still down, the workers are dying after startup
and the real error is only in the gunicorn error log, or from running the
unit's `ExecStart` line by hand:

```
$ cd ~/rhiven.talesofvalor.com
$ .venv/bin/gunicorn --workers 1 --bind=127.0.0.1:8099 passenger_wsgi:application
```

`systemctl --user status` will say `Worker failed to boot` and nothing more
useful, so go to the log or the command line rather than reading the unit
state.

### Why the database driver is the pure python one

`DATABASES` uses `mysql.connector.django`, not `django.db.backends.mysql`.
The latter goes through `mysqlclient`, a compiled extension linked against
`libmysqlclient`, which is exactly what the 26.04 upgrade broke. The pure
python connector needs nothing from the OS, so the same upgrade cannot
break it. It honours the `init_command` option the same way — checked
against the live database.

If you ever switch back to `mysqlclient` for speed, know that you are
taking on a rebuild every time DreamHost moves the OS forward.

### Rebuilding a virtualenv after an upgrade

The system python moves with the OS, so the venv has to be rebuilt against
whatever is now there:

```
$ cd ~/rhiven.stage.talesofvalor.com
$ rm -rf .venv
$ /usr/bin/python3 -m pip install --user --upgrade pipenv   # pipenv's own
$ pipenv --python /usr/bin/python3 sync                      # shebang breaks too
$ systemctl --user restart gunicorn
```

`pipenv` is installed with `--user` against a specific interpreter, so its
shebang breaks when that interpreter goes. Reinstall it before trying to
use it, or the error is a confusing `bad interpreter` rather than anything
about the venv.

## Gunicorn is bound to the public interface, not localhost

Worth knowing before changing anything about how gunicorn listens.

Both environments bind to their public hostname:

```
production   --bind=rhiven.talesofvalor.com:8000
stage        --bind=rhiven.stage.talesofvalor.com:8002
```

Both names resolve to `208.113.158.227`, the VPS's public IP, so gunicorn
listens on the public interface and **both ports are reachable from the open
internet**. Checked from outside:

```
208.113.158.227:8000   OPEN   HTTP 400
208.113.158.227:8002   OPEN   HTTP 302
```

This is not a mistake anyone made here. DreamHost's own article, *Using
linger with Gunicorn*, gives the template as `--bind=<example.com>:<port>`.
Following their documentation produces a publicly bound app server.

### What it cost us once

Scanners find the open port, connect by raw IP, and Django rejects the `Host`
header because the IP is not in production's `ALLOWED_HOSTS`. That is the
right answer, but every rejection used to write a full traceback:

```
django.core.exceptions.DisallowedHost: Invalid HTTP_HOST header: '208.113.158.227:8000'.
```

836,122 of them were 82% of a 793MB error log. `django.security.DisallowedHost`
now goes to a `NullHandler` in `settings/common.py`, so the request is still
refused but the traceback is not written down. The logs also rotate weekly.
That treats the symptom.

### The part still outstanding

`stage.py` has the IP **in** `ALLOWED_HOSTS`, which production does not:

```python
ALLOWED_HOSTS = [
    '208.113.158.227',          # production does not have this
    'rhiven.stage.talesofvalor.com',
    'rhiven.stage.static.talesofvalor.com',
]
```

So where production answers `400`, stage answers and serves the site:

```
http://208.113.158.227:8002/  ->  302  ->  /en/  ->  200
<title>Tales of Valor : Fellowship
```

Stage is publicly browsable over plain HTTP on a raw IP, bypassing the proxy
and TLS, and it holds a copy of real player data.

### The actual fix

Bind to localhost, so only the local proxy can reach gunicorn:

```
--bind=127.0.0.1:8000
```

This has **not** been done, deliberately. DreamHost's proxy sits in front, and
it is not visible from the server whether it forwards to the public hostname
or to `127.0.0.1`. If it forwards to the hostname and gunicorn stops
listening there, the site goes down. Ask DreamHost before changing it.

A smaller step that does not touch how gunicorn listens has been taken:
`'208.113.158.227'` is no longer in stage's `ALLOWED_HOSTS`, so stage now
answers `400` on raw-IP access the way production does. The port is still
open; stage just no longer serves anything to it.
