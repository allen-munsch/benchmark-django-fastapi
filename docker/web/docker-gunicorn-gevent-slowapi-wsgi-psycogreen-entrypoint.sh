#!/bin/sh
set -e
. /venv/bin/activate

/wait && gunicorn testdjango.wsgi_with_slow_api_mounted_psycogreen --workers 1 -k gevent --bind 0.0.0.0:8000 --timeout 520
#/wait && strace gunicorn testdjango.wsgi_with_slow_api_mounted_psycogreen --workers 1 -k gevent --bind 0.0.0.0:8000
