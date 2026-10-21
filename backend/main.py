import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.controllers import upload_controller
from app.core.config import settings
from app.core.database import engine, init_db
from app.core.redis_client import cache_ping

logging.basicConfig(level=settings.LOG_LEVEL)


# -------------------------------
# DB INIT
# -------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Energy Processor API", version="1.1.0", lifespan=lifespan)


# -------------------------------
# CORS (Streamlit)
# -------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------
# ROUTES
# -------------------------------
app.include_router(upload_controller.router, prefix="/api")


@app.get("/health", tags=["infra"])
def health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        database = "ok"
    except Exception:
        database = "erro"

    return {
        "status": "ok" if database == "ok" else "degradado",
        "database": database,
        "cache": "ok" if cache_ping() else "indisponível",
    }
