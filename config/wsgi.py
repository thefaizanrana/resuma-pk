"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()


def _ensure_db_migrated():
    """Best-effort migrations at cold start (serverless-safe).

    On platforms without a build-time migrate step (e.g. Vercel's Python
    runtime), applying migrations on first request keeps the app usable.
    Failures are swallowed so the request can still be served.
    """
    try:
        from django.core.management import call_command
        call_command("migrate", "--noinput")
    except Exception:
        pass


try:
    _ensure_db_migrated()
except Exception:
    pass
