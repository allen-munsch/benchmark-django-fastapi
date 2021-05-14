#!/bin/sh
set -e
. /venv/bin/activate

# errors out from lifespan, then ASGI_APPLICATION, then not able to find routing
/wait && uvicorn --lifespan on testdjango.asgi_from_channels:application
