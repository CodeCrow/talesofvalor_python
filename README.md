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

## Set up virtual environment

[Reference](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

[Install pip](http://https://pip.pypa.io/en/stable/installing/) (if it isn't installed already)

And make sure it is upgraded:

```
python3 -m pip install --user --upgrade pip
```

On Windows: 

```
talesofvalor_python.virtualenv\Scripts\python.exe -m pip install --upgrade pip
```


Tales of Valor will be using the virtual environment managment that comes with Python 3:


```
python3 -m venv .virtualenv

```
This will create a new directory inside the codebase that holds the workings for the virtual environment.

Activate the environment (which will have to be done each time you work on the codebase.

```
source .virtualenv/bin/activate

```

On Windows, use:

```
\.virtualenv\Scripts\activate.bat
```

The prompt should now change:

```
(.virtualenv)$
```

Install requirements

```
pip install -r requirements.txt
```

## Set up the database:

Start by creating a file named `.my.cnf` in your home directory (if you haven't already):

```
$ vim ~/.my.cnf
```

Next, paste the following block of text into the file replacing the user and password fields with your local MySQL credentials:

```
[client]
user = username_here
password = password_here
default-character-set = utf8
```

Save the file and close it.

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
```

## database syncing

Now run `syncdb` to ensure the database and local settings are set up correctly:

```
$ ./manage.py syncdb --settings=talesofvalor.settings.local
```

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

```
$ ./manage.py runserver --settings=talesofvalor.settings.local
```

Open a browser and go to [http://127.0.0.1:8000/admin/]()

You should now see a login screen!

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
4. Test user are under "accounts"

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

# Testing
## Setup
if you have not already, in the virtual environment that you have created for TOV, run the following pip install command
```
pip install selenium
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
