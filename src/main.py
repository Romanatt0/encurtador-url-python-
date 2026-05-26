from fastapi import FastAPI

from routes.shortener_routes import shortener_router
app = FastAPI(
    title="Encurtador-Url-API",
    description="API de serviça de encurtador de url",
    version="1.0.0",
)


app.include_router(shortener_router)