import pandas as pd

REQUIRED_COLUMNS = ["cliente", "consumo_kwh", "preco_mwh"]


def validate_columns(df):
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]

    if missing:
        raise ValueError(f"Colunas obrigatórias faltando: {missing}")
    
def validate_data(df):
    validate_columns(df)
    
    # verificar valores nulos só nas colunas obrigatórias
    # ('data' pode ser preenchida automaticamente e colunas extras são ignoradas)
    null_counts = df[REQUIRED_COLUMNS].isnull().sum()
    null_columns = null_counts[null_counts > 0]

    if not null_columns.empty:
        null_info = []
        for col, count in null_columns.items():
            null_info.append(f"{col}: {count} valores nulos")
        raise ValueError(f"Existem valores nulos no arquivo: {', '.join(null_info)}")

    # verificar tipos numéricos
    for col in ["consumo_kwh", "preco_mwh"]:
        convertido = pd.to_numeric(df[col], errors="coerce")
        invalidos = int(convertido.isnull().sum())
        if invalidos:
            raise ValueError(f"Coluna {col} possui {invalidos} valores não numéricos")
        df[col] = convertido

    # verificar valores negativos
    if (df["consumo_kwh"] < 0).any():
        neg_count = (df["consumo_kwh"] < 0).sum()
        raise ValueError(f"Consumo não pode ser negativo ({neg_count} valores encontrados)")

    if (df["preco_mwh"] < 0).any():
        neg_count = (df["preco_mwh"] < 0).sum()
        raise ValueError(f"Preço não pode ser negativo ({neg_count} valores encontrados)")