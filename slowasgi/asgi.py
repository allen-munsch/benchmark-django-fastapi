from fastapi import FastAPI
from a2wsgi import ASGIMiddleware

honk = FastAPI(title="Slower ASGI", version="42")

slow_app = ASGIMiddleware(honk)

@honk.get("/slowapi/")
async def root():
    return {"message": "Honk Honk"}

@honk.get("/slowapi/2/")
async def root():
    return {"message": "Honk Honk 2"}
