from datetime import datetime

import pandas as pd
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.cliente import Cliente
from app.models.consumo import Consumo
from app.repositories.cliente_repository import get_or_create_clientes


def _to_float(value):
    return float(value) if pd.notna(value) else 0.0


def _to_datetime(value):
    if value is None or pd.isna(value):
        return None

    parsed = pd.to_datetime(value, errors="coerce")
    # salva como datetime puro (sem string)
    return None if pd.isna(parsed) else parsed.to_pydatetime()


# -----------------------------------
# 💾 SALVAR CONSUMOS (UPLOAD)
# -----------------------------------
def save_consumos(db: Session, df: pd.DataFrame, upload_id: int | None = None, commit: bool = True):
    try:
        clientes = get_or_create_clientes(db, df["cliente"].astype(str).str.strip())
        tem_data = "data" in df.columns

        objetos = [
            Consumo(
                cliente_id=clientes[str(row["cliente"]).strip()].id,
                upload_id=upload_id,
                consumo_kwh=_to_float(row["consumo_kwh"]),
                preco_mwh=_to_float(row["preco_mwh"]),
                custo=_to_float(row["custo"]),
                data=_to_datetime(row["data"]) if tem_data else None,
            )
            for row in df.to_dict("records")
        ]

        db.add_all(objetos)
        if commit:
            db.commit()
        else:
            db.flush()

        return {
            "status": "success",
            "inserted": len(objetos)
        }

    except Exception as e:
        db.rollback()
        raise Exception(f"Erro ao salvar consumos: {str(e)}") from e


def delete_consumos_by_upload(db: Session, upload_id: int) -> int:
    return (
        db.query(Consumo)
        .filter(Consumo.upload_id == upload_id)
        .delete(synchronize_session=False)
    )


# -----------------------------------
# 📊 RELATÓRIO POR CLIENTE
# -----------------------------------
def get_relatorios(db: Session):
    results = (
        db.query(
            Cliente.nome,
            func.sum(Consumo.consumo_kwh).label("total_consumo"),
            func.sum(Consumo.custo).label("total_custo"),
            func.avg(Consumo.consumo_kwh).label("media_consumo"),
        )
        .join(Consumo, Consumo.cliente_id == Cliente.id)
        .group_by(Cliente.id, Cliente.nome)
        .all()
    )

    return [
        {
            "cliente": nome,
            "total_consumo": float(total_consumo or 0),
            "total_custo": float(total_custo or 0),
            "media_consumo": float(media_consumo or 0),
        }
        for nome, total_consumo, total_custo, media_consumo in results
    ]


# -----------------------------------
# 📦 LISTAGEM DETALHADA
# -----------------------------------
def get_consumos(
    db: Session,
    cliente: str | None = None,
    data_inicio: datetime | None = None,
    data_fim: datetime | None = None,
):
    query = db.query(Consumo, Cliente).join(Cliente, Consumo.cliente_id == Cliente.id)

    if cliente:
        query = query.filter(Cliente.nome == cliente)
    if data_inicio:
        query = query.filter(Consumo.data >= data_inicio)
    if data_fim:
        query = query.filter(Consumo.data <= data_fim)

    return [
        {
            "cliente": cliente.nome,
            "consumo_kwh": consumo.consumo_kwh,
            "preco_mwh": consumo.preco_mwh,
            "custo": consumo.custo,
            "data": consumo.data.isoformat() if consumo.data else None
        }
        for consumo, cliente in query.order_by(Consumo.data).all()
    ]
