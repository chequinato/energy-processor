from sqlalchemy.orm import Session
from sqlalchemy import func
import pandas as pd
from datetime import datetime

from app.models.consumo import Consumo
from app.models.cliente import Cliente
from app.repositories.cliente_repository import get_or_create_cliente


# -----------------------------------
# 💾 SALVAR CONSUMOS (UPLOAD)
# -----------------------------------
def save_consumos(db: Session, df: pd.DataFrame):
    try:
        objetos = []

        for _, row in df.iterrows():

            cliente = get_or_create_cliente(db, row["cliente"])

            # -----------------------------
            # normaliza números (proteção)
            # -----------------------------
            consumo_kwh = float(row["consumo_kwh"]) if pd.notna(row["consumo_kwh"]) else 0.0
            preco_mwh = float(row["preco_mwh"]) if pd.notna(row["preco_mwh"]) else 0.0
            custo = float(row["custo"]) if pd.notna(row["custo"]) else 0.0

            # -----------------------------
            # 🔥 FIX DEFINITIVO DA DATA
            # -----------------------------
            data = None
            if "data" in row and pd.notna(row["data"]):

                parsed = pd.to_datetime(row["data"], errors="coerce")

                if not pd.isna(parsed):
                    # IMPORTANTÍSSIMO:
                    # salva como datetime puro (sem string)
                    data = parsed.to_pydatetime()
                else:
                    data = None

            objetos.append(
                Consumo(
                    cliente_id=cliente.id,
                    consumo_kwh=consumo_kwh,
                    preco_mwh=preco_mwh,
                    custo=custo,
                    data=data
                )
            )

        db.add_all(objetos)
        db.commit()

        return {
            "status": "success",
            "inserted": len(objetos)
        }

    except Exception as e:
        db.rollback()
        raise Exception(f"Erro ao salvar consumos: {str(e)}")


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
def get_consumos(db: Session):
    dados = (
        db.query(Consumo, Cliente)
        .join(Cliente, Consumo.cliente_id == Cliente.id)
        .all()
    )

    return [
        {
            "cliente": cliente.nome,
            "consumo_kwh": consumo.consumo_kwh,
            "preco_mwh": consumo.preco_mwh,
            "custo": consumo.custo,
            "data": consumo.data.isoformat() if consumo.data else None
        }
        for consumo, cliente in dados
    ]