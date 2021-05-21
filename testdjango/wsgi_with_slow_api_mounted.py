import os

from django.core.wsgi import get_wsgi_application

from werkzeug.middleware.dispatcher import DispatcherMiddleware
from slowasgi.asgi import slow_app
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testdjango.settings')

legacy_app = get_wsgi_application()

# from routes import Mapper
# modified from https://github.com/benoitc/gunicorn/blob/cf55d2cec277f220ebd605989ce78ad1bb553c46/examples/multiapp.py
# class Application(object):
#     def __init__(self):
#         self.map = Mapper()
#         self.map.connect('application', '/', app=legacy_app)
#         self.map.connect('slowasgi', '/slowasgi', app=slow_app)
#
#     def __call__(self, environ, start_response):
#         match = self.map.routematch(environ=environ)
#         import pdb;pdb.set_trace()
#         # oops index
#         return match[0]['app'](environ, start_response)

application = DispatcherMiddleware(legacy_app,
                                   {'/slowapi': slow_app})
