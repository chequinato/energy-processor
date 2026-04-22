from fastapi import FastAPI
from app.controllers import upload_controller

app = FastAPI()

app.include_router(upload_controller.router)