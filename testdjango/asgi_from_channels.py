import os
import django
from channels.routing import get_default_application
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testdjango.settings')

django.setup()

application = ASGIStaticFilesHandler(get_default_application())

