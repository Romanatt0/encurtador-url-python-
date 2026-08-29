from fastapi import FastAPI
import os

from routes.shortener_routes import shortener_router
from routes.metrics_routes import metrics_router
from routes.user_routes import user_router
from fastapi.middleware.cors import CORSMiddleware
from slowapi.middleware import SlowAPIMiddleware

from core.rate_limiter import limiter, setup_rate_limit

_cors_origins = [o.strip() for o in os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
).split(",") if o.strip()]
_api_base = os.getenv("API_BASE_URL", "http://localhost:8000")

app = FastAPI(
    title="Encurtador-Url-API",
    description="API de serviço de encurtador de url",
    version="1.0.0",
    servers=[
        {"url": _api_base}
    ]

)

setup_rate_limit(app)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://romanatto-encurtador.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(shortener_router)
app.include_router(metrics_router)
app.include_router(user_router)
