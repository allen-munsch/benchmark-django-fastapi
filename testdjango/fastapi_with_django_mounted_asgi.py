import os

from django.core.asgi import get_asgi_application
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler
from slowasgi.asgi import honk
print(f"RUNNING: __name__: {__name__}")

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testdjango.settings')
django_app = ASGIStaticFilesHandler(get_asgi_application())
application = honk
application.mount('/', django_app)
