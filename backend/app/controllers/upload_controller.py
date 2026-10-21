import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.redis_client import cache_delete, cache_get, cache_set
from app.models.cliente import Cliente
from app.models.upload import Upload
from app.repositories.consumo_repository import delete_consumos_by_upload
from app.repositories.consumo_repository import get_consumos as get_consumos_repo
from app.schemas.consumo import Relatorio, ResumoResponse, UploadResponse
from app.services.consumo_service import get_relatorios_service, get_resumo_service, process_file
from app.utils.file_reader import SUPPORTED_EXTENSIONS, read_file

logger = logging.getLogger(__name__)

router = APIRouter()

DbSession = Annotated[Session, Depends(get_db)]

CACHE_KEYS = ("relatorios", "relatorios_resumo")


def _safe_filename(filename: str) -> str:
    # descarta diretórios (evita path traversal) e caracteres estranhos
    nome = Path(filename).name
    return re.sub(r"[^\w.\- ]", "_", nome) or "arquivo"


# -------------------------------
# 📤 UPLOAD
# -------------------------------
@router.post("/upload")
async def upload_file(
    file: Annotated[UploadFile, File()],
    db: DbSession,
):
    filename = _safe_filename(file.filename or "")

    if Path(filename).suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Formato não suportado: use CSV ou XLSX")

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    content = await file.read(max_bytes + 1)
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"Arquivo maior que o limite de {settings.MAX_UPLOAD_SIZE_MB} MB"
        )

    try:
        df = read_file(content, filename)

        # upload e consumos são gravados na mesma transação
        upload = Upload(filename=filename)
        db.add(upload)
        db.flush()

        metrics = process_file(db, df, upload_id=upload.id, commit=False)
        db.commit()
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        db.rollback()
        logger.exception("Falha ao processar upload %s", filename)
        raise HTTPException(status_code=500, detail="Erro ao processar arquivo") from e

    # guarda uma cópia do arquivo original, prefixada pelo id do upload
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    (upload_dir / f"{upload.id}_{filename}").write_bytes(content)

    cache_delete(*CACHE_KEYS)

    return {
        "upload_id": upload.id,
        "filename": filename,
        "columns": list(df.columns),
        # to_json lida com NaN e datas; to_dict quebraria a serialização
        "rows_preview": json.loads(df.head(5).to_json(date_format="iso")),
        "metrics": metrics
    }


# -------------------------------
# 📊 CONSUMOS
# -------------------------------
@router.get("/consumos")
def get_consumos(
    db: DbSession,
    cliente: str | None = None,
    data_inicio: datetime | None = None,
    data_fim: datetime | None = None,
):
    return get_consumos_repo(db, cliente=cliente, data_inicio=data_inicio, data_fim=data_fim)


# -------------------------------
# 👥 CLIENTES
# -------------------------------
@router.get("/clientes", response_model=list[str])
def get_clientes(db: DbSession):

    clientes = db.query(Cliente.nome).order_by(Cliente.nome).all()
    return [c[0] for c in clientes]


# -------------------------------
# 📈 RELATÓRIOS
# -------------------------------
@router.get("/relatorios", response_model=list[Relatorio])
def get_relatorios(db: DbSession):
    cache_key = "relatorios"

    cached = cache_get(cache_key)
    if cached is not None:
        logger.debug("relatorios veio do cache")
        return cached

    data = get_relatorios_service(db)
    cache_set(cache_key, data)

    return data


@router.get("/relatorios/resumo", response_model=ResumoResponse)
def get_relatorios_resumo(db: DbSession):

    cache_key = "relatorios_resumo"

    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    data = get_resumo_service(db)
    cache_set(cache_key, data)

    return data


# -------------------------------
# 📁 UPLOADS
# -------------------------------
@router.get("/uploads", response_model=list[UploadResponse])
def list_uploads(db: DbSession):
    return db.query(Upload).order_by(Upload.created_at.desc()).all()


@router.delete("/uploads/{upload_id}")
def delete_upload(upload_id: int, db: DbSession):

    upload = db.get(Upload, upload_id)

    if not upload:
        raise HTTPException(status_code=404, detail="Upload não encontrado")

    # remove também os consumos importados por esse upload
    removidos = delete_consumos_by_upload(db, upload_id)
    db.delete(upload)
    db.commit()

    # 🔥 limpa cache
    cache_delete(*CACHE_KEYS)

    return {"message": "Deletado com sucesso", "consumos_removidos": removidos}
