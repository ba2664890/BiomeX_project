#!/usr/bin/env sh
set -e

python manage.py makemigrations --noinput
python manage.py migrate --noinput --run-syncdb
python manage.py collectstatic --noinput

exec gunicorn biomex.wsgi:application \
  --bind 0.0.0.0:${PORT:-10000} \
  --workers ${WEB_CONCURRENCY:-2} \
  --timeout ${GUNICORN_TIMEOUT:-120}
