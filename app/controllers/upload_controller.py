from fastapi import APIRouter, UploadFile, File
import pandas as pd
import os
from app.models.consumo import Consumo
from app.models.cliente import Cliente
from app.utils.validators import validate_columns, validate_data
from app.utils.calculations import calculate_metrics
from app.core.database import SessionLocal
from app.repositories.consumo_repository import save_consumos

router = APIRouter()

UPLOAD_DIR = "data/uploads"

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    
    # garantir que a pasta existe
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # salvar arquivo
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # ler com pandas
    if file.filename.endswith(".csv"):
        df = pd.read_csv(file_path)
    elif file.filename.endswith(".xlsx"):
        df = pd.read_excel(file_path)
    else:
        return {"error": "Formato não suportado"}

    # validar colunas
    validate_columns(df)

    # validar dados
    validate_data(df)

    # calcular métricas
    metrics = calculate_metrics(df)

    # salvar dados no banco
    db = SessionLocal()
    try:
        save_consumos(db, df) 
    finally:
        db.close()

    # retornar preview
    return {
        "filename": file.filename,
        "columns": list(df.columns),
        "rows_preview": df.head(5).to_dict(),
        "metrics": metrics
    }

from app.models.consumo import Consumo
from app.models.cliente import Cliente

@router.get("/consumos")
def get_consumos():
    db = SessionLocal()

    dados = db.query(Consumo, Cliente).join(
        Cliente, Consumo.cliente_id == Cliente.id
    ).all()

    db.close()

    return [
        {
            "cliente": cliente.nome,
            "consumo_kwh": consumo.consumo_kwh,
            "preco_mwh": consumo.preco_mwh,
            "custo": consumo.custo
        }
        for consumo, cliente in dados
    ]

