from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import date

class ConsumoBase(BaseModel):
    cliente: str
    consumo_kwh: float
    preco_mwh: float

class ConsumoCreate(ConsumoBase):
    data: Optional[date] = None  # for trends

class ConsumoResponse(ConsumoBase):
    id: int
    custo: float
    data: Optional[date] = None
    cliente_id: int

    class Config:
        from_attributes = True

class Metrics(BaseModel):
    total_consumo: float
    total_custo: float

class Relatorio(BaseModel):
    cliente: str
    total_consumo: float
    total_custo: float
    media_consumo: float

class RelatoriosResponse(BaseModel):
    data: List[Relatorio]

