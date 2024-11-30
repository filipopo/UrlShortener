#!/bin/sh

python manage.py migrate --noinput

if echo "$BUILD" | grep -q "nginx$"; then
  nginx &
fi

gunicorn --bind 0.0.0.0:8000 urlshortener.wsgi