
def validate_columns(df):
    required_columns = ["cliente", "consumo_kwh", "preco_mwh"]

    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        raise ValueError(f"Colunas obrigatórias faltando: {missing}")
    
def validate_data(df):
    validate_columns(df)
    
    # verificar valores nulos com detalhes (ignorando coluna 'data')
    null_counts = df.isnull().sum()
    null_columns = null_counts[null_counts > 0]
    
    # Remover 'data' da verificação de nulos (pode ser preenchida automaticamente)
    if 'data' in null_columns:
        null_columns = null_columns.drop('data')
    
    if not null_columns.empty:
        null_info = []
        for col, count in null_columns.items():
            null_info.append(f"{col}: {count} valores nulos")
        raise ValueError(f"Existem valores nulos no arquivo: {', '.join(null_info)}")

    # verificar valores negativos
    if (df["consumo_kwh"] < 0).any():
        neg_count = (df["consumo_kwh"] < 0).sum()
        raise ValueError(f"Consumo não pode ser negativo ({neg_count} valores encontrados)")

    if (df["preco_mwh"] < 0).any():
        neg_count = (df["preco_mwh"] < 0).sum()
        raise ValueError(f"Preço não pode ser negativo ({neg_count} valores encontrados)")