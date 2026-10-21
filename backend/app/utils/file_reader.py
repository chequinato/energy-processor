import logging
from io import BytesIO
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".csv", ".xlsx"}


def read_file(source, filename: str | None = None) -> pd.DataFrame:
    """
    Lê um CSV/XLSX a partir de um caminho no disco ou do conteúdo em bytes.
    Quando `source` são bytes, `filename` define o formato pela extensão.
    """
    if isinstance(source, (bytes, bytearray)):
        if not filename:
            raise ValueError("Informe o nome do arquivo para identificar o formato")
        extension = Path(filename).suffix.lower()
        content = BytesIO(source)
    else:
        path = Path(source)
        if not path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {source}")
        extension = path.suffix.lower()
        content = path

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError("Formato não suportado: use CSV ou XLSX")

    try:
        if extension == ".csv":
            df = pd.read_csv(content)
        else:
            df = pd.read_excel(content)
    except Exception as e:
        raise ValueError(f"Erro ao ler arquivo: {str(e)}") from e

    if df.empty:
        raise ValueError("Arquivo vazio")

    # 🔥 TRATAMENTO DE DATA
    if "data" in df.columns:
        df["data"] = pd.to_datetime(df["data"], errors="coerce", dayfirst=True)

        # Preencher datas nulas com data atual
        null_count = int(df["data"].isnull().sum())
        if null_count:
            df["data"] = df["data"].fillna(pd.Timestamp.now())
            logger.info("Preenchidas %s datas nulas com data atual", null_count)

    return df
