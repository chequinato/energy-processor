
from sqlalchemy import Column, Integer, String, Float
from app.core.database import Base

class Consumo(Base):
    __tablename__ = "consumos"

    id = Column(Integer, primary_key=True, index=True)
    cliente = Column(String)
    consumo_kwh = Column(Float)
    preco_mwh = Column(Float)
    custo = Column(Float)