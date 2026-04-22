from fastapi import APIRouter, UploadFile, File
import pandas as pd
import os
from app.utils.validators import validate_columns, validate_data

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

    # retornar preview
    return {
        "filename": file.filename,
        "columns": list(df.columns),
        "rows_preview": df.head(5).to_dict()
    }