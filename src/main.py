from fastapi import FastAPI

from routes.shortener_routes import shortener_router
from routes.metrics_routes import metrics_router
from fastapi.middleware.cors import CORSMiddleware
from slowapi.middleware import SlowAPIMiddleware

from core.rate_limiter import limiter, setup_rate_limit
app = FastAPI(
    title="Encurtador-Url-API",
    description="API de serviça de encurtador de url",
    version="1.0.0",
        servers=[
        {"url": "http://localhost:8000"}
    ]

)

setup_rate_limit(app)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware, 
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000/docs",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(shortener_router)
app.include_router(metrics_router)
