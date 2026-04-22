from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
import os

from app.core.database import get_db
from app.services.consumo_service import process_file, get_relatorios_service
from app.utils.file_reader import read_file

from app.models.consumo import Consumo
from app.models.cliente import Cliente

router = APIRouter()

UPLOAD_DIR = "data/uploads"


# -------------------------------
# 📤 UPLOAD
# -------------------------------
@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    df = read_file(file_path)

    metrics = process_file(db, df)

    return {
        "filename": file.filename,
        "columns": list(df.columns),
        "rows_preview": df.head(5).to_dict(),
        "metrics": metrics
    }


# -------------------------------
# 📊 CONSUMOS
# -------------------------------
@router.get("/consumos")
def get_consumos(db: Session = Depends(get_db)):

    dados = db.query(Consumo, Cliente).join(
        Cliente, Consumo.cliente_id == Cliente.id
    ).all()

    return [
        {
            "cliente": cliente.nome,
            "consumo_kwh": consumo.consumo_kwh,
            "preco_mwh": consumo.preco_mwh,
            "custo": consumo.custo,
            "data": consumo.data
        }
        for consumo, cliente in dados
    ]


# -------------------------------
# 👥 CLIENTES
# -------------------------------
@router.get("/clientes")
def get_clientes(db: Session = Depends(get_db)):

    clientes = db.query(Cliente.nome).distinct().all()
    return [c[0] for c in clientes]


# -------------------------------
# 📈 RELATÓRIOS
# -------------------------------
@router.get("/relatorios")
def get_relatorios(db: Session = Depends(get_db)):
    return get_relatorios_service(db)


@router.get("/relatorios/resumo")
def get_relatorios_resumo(db: Session = Depends(get_db)):

    relatorios = get_relatorios_service(db)

    return {
        "total_clientes": len(relatorios),
        "total_geral_consumo": sum(r["total_consumo"] for r in relatorios),
        "total_geral_custo": sum(r["total_custo"] for r in relatorios)
    }