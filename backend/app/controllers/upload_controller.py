from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from sqlalchemy.orm import Session
import os

from app.core.database import get_db
from app.services.consumo_service import process_file, get_relatorios_service
from app.utils.file_reader import read_file

from app.models.consumo import Consumo
from app.models.cliente import Cliente
from datetime import datetime
from app.models.upload import Upload
import json
from app.core.redis_client import redis_client


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

    # 🔥 SALVAR UPLOAD NO BANCO
    upload = Upload(
        filename=file.filename,
        created_at=datetime.utcnow()
    )

    db.add(upload)
    db.commit()

    redis_client.delete("relatorios")
    redis_client.delete("relatorios_resumo")

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
            "data": consumo.data.isoformat() if consumo.data else None
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
    cache_key = "relatorios"

    cached = redis_client.get(cache_key)
    if cached:
        print("VEIO DO CACHE")
        return json.loads(cached)

    data = get_relatorios_service(db)
    redis_client.setex(cache_key, 60, json.dumps(data))

    return data


@router.get("/relatorios/resumo")
def get_relatorios_resumo(db: Session = Depends(get_db)):

    cache_key = "relatorios_resumo"

    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    relatorios = get_relatorios_service(db)

    data = {
        "total_clientes": len(relatorios),
        "total_geral_consumo": sum(r["total_consumo"] for r in relatorios),
        "total_geral_custo": sum(r["total_custo"] for r in relatorios)
    }

    redis_client.setex(cache_key, 60, json.dumps(data))

    return data

@router.get("/uploads")
def list_uploads(db: Session = Depends(get_db)):
    uploads = db.query(Upload).order_by(Upload.created_at.desc()).all()

    return [
        {
            "id": u.id,
            "filename": u.filename,
            "created_at": u.created_at
        }
        for u in uploads
    ]

@router.delete("/uploads/{upload_id}")
def delete_upload(upload_id: int, db: Session = Depends(get_db)):

    upload = db.query(Upload).filter(Upload.id == upload_id).first()

    if not upload:
        raise HTTPException(status_code=404, detail="Upload não encontrado")

    db.delete(upload)
    db.commit()

    # 🔥 limpa cache
    redis_client.delete("relatorios")
    redis_client.delete("relatorios_resumo")

    return {"message": "Deletado com sucesso"}