from fastapi import APIRouter, UploadFile, File
import pandas as pd
import os

from app.core.database import SessionLocal
from app.services.consumo_service import process_file
from app.models.consumo import Consumo
from app.models.cliente import Cliente

router = APIRouter()

UPLOAD_DIR = "data/uploads"


# -------------------------------
# 📤 UPLOAD
# -------------------------------
@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    # garantir pasta
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # salvar arquivo
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # ler arquivo
    if file.filename.endswith(".csv"):
        df = pd.read_csv(file_path)
    elif file.filename.endswith(".xlsx"):
        df = pd.read_excel(file_path)
    else:
        return {"error": "Formato não suportado"}

    # 🔥 processar (SERVICE FAZ TUDO)
    db = SessionLocal()
    try:
        metrics = process_file(db, df)
    finally:
        db.close()

    return {
        "filename": file.filename,
        "columns": list(df.columns),
        "rows_preview": df.head(5).to_dict(),
        "metrics": metrics
    }


# -------------------------------
# 📊 GET CONSUMOS
# -------------------------------
@router.get("/consumos")
def get_consumos():
    db = SessionLocal()

    try:
        dados = db.query(Consumo, Cliente).join(
            Cliente, Consumo.cliente_id == Cliente.id
        ).all()

        return [
            {
                "cliente": cliente.nome,
                "consumo_kwh": consumo.consumo_kwh,
                "preco_mwh": consumo.preco_mwh,
                "custo": consumo.custo
            }
            for consumo, cliente in dados
        ]

    finally:
        db.close()