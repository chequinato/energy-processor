def calculate_metrics(df):
    df["custo"] = df["consumo_kwh"] * df["preco_mwh"] / 1000

    total_consumo = int(df["consumo_kwh"].sum())
    total_custo = float(df["custo"].sum())

    return {
        "total_consumo": total_consumo,
        "total_custo": total_custo
    }