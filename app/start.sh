#!/bin/sh

python manage.py migrate --noinput

if [ "$BUILD" = "nginx" ]; then
  nginx &
fi

gunicorn --bind 0.0.0.0:8000 urlshortener.wsgi