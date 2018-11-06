"""
WSGI config for diseraca project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "diseraca.settings")
#sys.path.append('/path/to/your/django/directory/django_project')
#sys.path.append('/path/to/your/django/directory')
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
