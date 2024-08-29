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
## Setup
if you have not already, in the virtual environment that you have created for TOV, run the following pip install commands
```
pip install selenium
pip install --upgrade mailosaur
```
This will install the packaged needed to interface with a webdriver. For now there is a instance of chrome included in the repo.

## Note: below instructions are for a windows machine
1. Open project in VSCode
2. Click 'View' > 'Terminal'
3. In the terminal that opens in VSCode start the server using above method
4. In the upper right hand side of the terminal click the dropdown and start a new terminal of your choice (I typically use CMD, but Powershell will also work)
5. In the new terminal run
```
python .\talesofvalor\tests\SimpleTests.py
```
6. A instance of chrome should then open and attempt to log in to the sever as well as run other tests
7. At the end of the tests you will see something to the effect of the following if all the tests passed otherwise you will get messages saying which tests failed. 
```
----------------------------------------------------------------------
Ran 3 tests in 14.240s

OK
```
