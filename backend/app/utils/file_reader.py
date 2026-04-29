import pandas as pd
import os
from typing import Tuple
from pathlib import Path

def read_file(file_path: str) -> pd.DataFrame:
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
    
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path)
        else:
            raise ValueError("Formato não suportado: use CSV ou XLSX")
        
        if df.empty:
            raise ValueError("Arquivo vazio")

        # 🔥 TRATAMENTO DE DATA
        if "data" in df.columns:
            df["data"] = pd.to_datetime(df["data"], errors="coerce", dayfirst=True)
            
            # Preencher datas nulas com data atual
            if df["data"].isnull().any():
                null_count = df["data"].isnull().sum()
                df["data"] = df["data"].fillna(pd.Timestamp.now())
                print(f"Preenchidas {null_count} datas nulas com data atual")

        return df

    except Exception as e:
        raise ValueError(f"Erro ao ler arquivo: {str(e)}")

