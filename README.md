# Installation

## Get the code
Clone Repository 
https://github.com/CodeCrow/talesofvalor_python

```
$ git clone https://github.com/CodeCrow/talesofvalor_python.git
$ cd talesofvalor_python
```


## Set up virtual environment

[Install pip](http://https://pip.pypa.io/en/stable/installing/) (if it isn't installed already)

[Install virtualenv](https://virtualenv.pypa.io/en/stable/installation/)

```
$ pip install virtualenv
```

[Install virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/) if you don't have it. (it makes things easier)

```
$ pip install virtualenvwrapper
```

Set up the home directory that stores the environment.
Change "~/Envs" to whatever directory you would prefer.


```
$ export WORKON_HOME=~/Envs
$ mkdir -p $WORKON_HOME

```

Start up ```virtualenvwrapper``` (should happen be default on next login)


```
$ source /usr/local/bin/virtualenvwrapper.sh
```

Create the environment to work in:

```
$ mkvirtualenv talesofvalor
```

The prompt should now change:

```
(talesofvalor)$
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

Where “environment” is “stage”, “production”, “development”, and “branch_name” is the branch that should be deployed that should be deployed.

Example:
`fab deploy --environment stage --migrate`

This would would deploy the latest default staging branch to the 'stage' environment and run existing migrations.


# Database Info

MySQL now defaults to using INNO DB as the storage engine, which is awesome, except it throws constraints around like candy, which doesn't play well with plugins.  So we sometimes have to remove the constraints.

Example Error: 

``IntegrityError: (1452, 'Cannot add or update a child row: a foreign key constraint fails (`spldjangocms`.`video_splvideoasset`, CONSTRAINT `cmsplugin_ptr_id_refs_id_20f5c1c6` FOREIGN KEY (`cmsplugin_ptr_id`) REFERENCES `cms_cmsplugin` (`id`))')``

To fix the error, you can either remove the constrait using a GUI such as [Sequel Pro](http://www.sequelpro.com/) or the following command:

``ALTER TABLE video_splvideoasset DROP FOREIGN KEY 'cmsplugin_ptr_id';``