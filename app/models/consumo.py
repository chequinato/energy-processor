from sqlalchemy import Column, Integer, Float, ForeignKey, Date
from sqlalchemy.sql import func
from app.core.database import Base
from sqlalchemy import DateTime


class Consumo(Base):
    __tablename__ = "consumos"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    consumo_kwh = Column(Float)
    preco_mwh = Column(Float)
    custo = Column(Float)
    data = Column(DateTime, server_default=func.now())  # default today for trends
