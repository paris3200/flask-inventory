[![Build Status](https://travis-ci.org/paris3200/flask-inventory.svg)](https://travis-ci.org/paris3200/flask-inventory) [![Coverage Status](https://coveralls.io/repos/paris3200/flask-inventory/badge.svg?branch=master&service=github)](https://coveralls.io/github/paris3200/flask-inventory?branch=master)

# Flask Inventory

Flask Inventory is an attempt to create an inventory management system for
a small business using the flask framework.  Currently the project is under heavy
development and not ready for use.    



## Quick Start

### Basics

1. Activate a virtualenv
1. Install the requirements
```sh
$ pip install -r requirements.txt
```

### Set Environment Variables

Update *config.py*, and then run:

```sh
$ export APP_SETTINGS="config.DevConfig"
```

### Create DB

Run _setup.sh_ to setup the database and add an admin user.  

```sh
$  ./setup.sh
```

### Run the Application

Start the webserver:

```sh
$ python manage.py runserver
```

You should then be able to view the application in the brower.  To access the admin section login with:

Username: ad@min.com

Password: admin_user

### Testing

Without coverage:

```sh
$ python manage.py test
```

With coverage:

```sh
$ python manage.py cov
```
