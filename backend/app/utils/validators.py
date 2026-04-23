
def validate_columns(df):
    required_columns = ["cliente", "consumo_kwh", "preco_mwh"]

    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        raise ValueError(f"Colunas obrigatórias faltando: {missing}")
    
def validate_data(df):
    validate_columns(df)
    # verificar valores nulos
    if df.isnull().any().any():
        raise ValueError("Existem valores nulos no arquivo")

    # verificar valores negativos
    if (df["consumo_kwh"] < 0).any():
        raise ValueError("Consumo não pode ser negativo")

    if (df["preco_mwh"] < 0).any():
        raise ValueError("Preço não pode ser negativo")