#!/bin/sh

python manage.py migrate --noinput

gunicorn --bind 0.0.0.0:8000 urlshortener.wsgi