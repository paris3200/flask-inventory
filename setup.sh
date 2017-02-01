#!/bin/bash

# Creates the initial development database and adds the default admin user.  

python manage.py create_db
python manage.py db init
python manage.py db migrate
python manage.py create_admin
