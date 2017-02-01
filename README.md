[![Build Status](https://travis-ci.org/paris3200/flask-inventory.svg)](https://travis-ci.org/paris3200/flask-inventory) [![Coverage Status](https://coveralls.io/repos/paris3200/flask-inventory/badge.svg?branch=master&service=github)](https://coveralls.io/github/paris3200/flask-inventory?branch=master)

# Flask Inventory

Flask Inventory is an attempt to create an inventory management system for
a small business using the flask framework.  Currently the project is under heavy
development.  



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
$ export APP_SETTINGS="project.config.DevelopmentConfig"
```

### Create DB

Run _setup.sh_ to setup the database. 

```sh
$  ./setup.sh
```

### Run the Application

```sh
$ python manage.py runserver
```

### Testing

Without coverage:

```sh
$ python manage.py test
```

With coverage:

```sh
$ python manage.py cov
```
