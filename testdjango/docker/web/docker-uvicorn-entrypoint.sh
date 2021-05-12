#!/bin/sh
set -e
. /venv/bin/activate

/wait && uvicorn testdjango.asgi:application
