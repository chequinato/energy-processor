from fastapi import FastAPI
from app.controllers import upload_controller
from app.core.database import Base, engine
from app.models.consumo import Consumo

app = FastAPI()

app.include_router(upload_controller.router)

Base.metadata.create_all(bind=engine)