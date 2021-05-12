import os

from django.core.wsgi import get_wsgi_application
from dj_static import Cling
from uvicorn.middleware.wsgi import WSGIMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testdjango.settings')

application = WSGIMiddleware(
    Cling(get_wsgi_application()), workers=10
)
