import os
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'testdjango.settings'
django.setup()
# from django.conf import settings
# settings.configure()

from asgiref.sync import sync_to_async
from fastapi import FastAPI
from a2wsgi import ASGIMiddleware
from clowncollege.models import ClownCollege
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

honk = FastAPI(title="Slower ASGI", version="42")

# import asyncio
# import aiogevent
#
# asyncio.set_event_loop_policy(aiogevent.EventLoopPolicy())
# loop = asyncio.get_event_loop()

slow_app = ASGIMiddleware(honk)

@honk.get("/slowapi/")
async def root():
    return {"message": "Honk Honk"}


@honk.get("/slowapi/django-async-orm/closure/")
async def root():
    try:
        async def closure():
            return [honks.id for honks in await ClownCollege.objects.async_all()]
        return await closure()
    except Exception as e:
        logger.debug(e)
        raise


@honk.get("/slowapi/sleep/")
async def root():
    try:
        result = await ClownCollege.objects.async_raw('SELECT 1 as id, clock_timestamp() as t1, pg_sleep(1) as t2, clock_timestamp() as t3;')
        return str([(x.id, x.t1, x.t2, x.t3) for x in result])
    except Exception as e:
        logger.debug(e)
        raise

@honk.get("/slowapi/django-async-orm/")
async def root():
    try:
        return [honks.id for honks in await ClownCollege.objects.async_all()]
    except Exception as e:
        logger.debug(e)
        raise
