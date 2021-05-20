#!/bin/sh
set -e
. /venv/bin/activate

/wait && gunicorn testdjango.wsgi --workers 1 -k gevent --bind 0.0.0.0:8000
