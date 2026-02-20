#!/usr/bin/env sh
set -e

python manage.py makemigrations --noinput

python - <<'PY'
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "biomex.settings")

import django

django.setup()

from django.db import connection

tables_by_app = {
    "contenttypes": "django_content_type",
    "auth": "auth_group",
    "sessions": "django_session",
    "admin": "django_admin_log",
    "users": "users_user",
}

with connection.cursor() as cursor:
    cursor.execute("SELECT to_regclass('django_migrations')")
    has_migration_table = cursor.fetchone()[0] is not None
    if not has_migration_table:
        print("No django_migrations table yet; first migration run.")
    else:
        apps_to_reset = []
        for app, table_name in tables_by_app.items():
            cursor.execute("SELECT to_regclass(%s)", [table_name])
            table_exists = cursor.fetchone()[0] is not None
            if not table_exists:
                apps_to_reset.append(app)

        if apps_to_reset:
            print(f"Repairing migration history for apps: {', '.join(apps_to_reset)}")
            cursor.execute(
                "DELETE FROM django_migrations WHERE app = ANY(%s)",
                [apps_to_reset],
            )
        else:
            print("Migration history and core tables are consistent.")
PY

python manage.py migrate --noinput --run-syncdb --fake-initial
python manage.py collectstatic --noinput

exec gunicorn biomex.wsgi:application \
  --bind 0.0.0.0:${PORT:-10000} \
  --workers ${WEB_CONCURRENCY:-2} \
  --timeout ${GUNICORN_TIMEOUT:-120}
