from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.sql import func

from app.core.database import Base


class Consumo(Base):
    __tablename__ = "consumos"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    # upload de origem: permite remover os consumos junto com o upload
    upload_id = Column(Integer, ForeignKey("uploads.id"), nullable=True, index=True)
    consumo_kwh = Column(Float)
    preco_mwh = Column(Float)
    custo = Column(Float)
    data = Column(DateTime, server_default=func.now())  # default today for trends
