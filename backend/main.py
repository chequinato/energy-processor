from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.controllers import upload_controller
from app.core.database import Base, engine

app = FastAPI(title="Energy Processor API", version="1.0.0")


# -------------------------------
# CORS (Streamlit)
# -------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------
# ROUTES
# -------------------------------
app.include_router(upload_controller.router, prefix="/api")


# -------------------------------
# DB INIT
# -------------------------------
Base.metadata.create_all(bind=engine)