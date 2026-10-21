from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class ConsumoBase(BaseModel):
    cliente: str
    consumo_kwh: float
    preco_mwh: float


class ConsumoCreate(ConsumoBase):
    data: date | None = None  # for trends


class ConsumoResponse(ConsumoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    custo: float
    data: date | None = None
    cliente_id: int


class Metrics(BaseModel):
    total_consumo: float
    total_custo: float


class Relatorio(BaseModel):
    cliente: str
    total_consumo: float
    total_custo: float
    media_consumo: float


class RelatoriosResponse(BaseModel):
    data: list[Relatorio]


class ResumoResponse(BaseModel):
    total_clientes: int
    total_geral_consumo: float
    total_geral_custo: float


class UploadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    created_at: datetime | None = None
