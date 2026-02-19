"""
ASGI config for biomex project.
"""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'biomex.settings')

application = get_asgi_application()
