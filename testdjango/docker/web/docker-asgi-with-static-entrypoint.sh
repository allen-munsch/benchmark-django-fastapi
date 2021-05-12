#!/bin/sh
set -e
. /venv/bin/activate

/wait && gunicorn --workers 1 testdjango.asgi_with_static --log-level=debug -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
