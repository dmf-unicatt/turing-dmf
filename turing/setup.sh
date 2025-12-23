#!/bin/bash

VENV="./django_venv"

if [ ! -d $VENV ]; then
    python3 -m venv $VENV
    . $VENV/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    cp Turing/settings.ini.example Turing/settings.ini

    python manage.py makemigrations
    python manage.py makemigrations engine
    python manage.py migrate
    echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', '', 'admin')" | python manage.py shell
else
    . $VENV/bin/activate
fi

python manage.py runserver 0.0.0.0:8000
