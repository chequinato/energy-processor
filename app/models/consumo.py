
from sqlalchemy import Column, Integer, Float, ForeignKey
from app.core.database import Base

class Consumo(Base):
    __tablename__ = "consumos"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    consumo_kwh = Column(Float)
    preco_mwh = Column(Float)
    custo = Column(Float)