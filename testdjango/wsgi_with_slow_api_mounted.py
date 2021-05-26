import os

from django.core.wsgi import get_wsgi_application

from werkzeug.middleware.dispatcher import DispatcherMiddleware
from slowasgi.asgi import slow_app
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testdjango.settings')

legacy_app = get_wsgi_application()

application = DispatcherMiddleware(legacy_app,
                                   {'/slowapi': slow_app})
