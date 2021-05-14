import os

from fastapi import FastAPI
from django.core.asgi import get_asgi_application
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testdjango.settings')

django_app = ASGIStaticFilesHandler(get_asgi_application())
application = FastAPI()
application.mount('/', django_app)
