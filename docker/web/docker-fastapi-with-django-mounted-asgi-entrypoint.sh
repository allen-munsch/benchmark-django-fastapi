#!/bin/sh
set -e
. /venv/bin/activate

/wait && gunicorn --workers 1 testdjango.fastapi_with_django_mounted_asgi --log-level=debug -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
