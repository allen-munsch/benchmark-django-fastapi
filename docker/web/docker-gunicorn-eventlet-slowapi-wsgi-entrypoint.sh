#!/bin/sh
set -e
. /venv/bin/activate

/wait && gunicorn testdjango.wsgi_with_slow_api_mounted --workers 1 -k eventlet --bind 0.0.0.0:8000
