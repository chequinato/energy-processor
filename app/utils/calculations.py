
def calculate_metrics(df):
    df["custo"] = df["consumo_kwh"] * df["preco_mwh"] / 1000

    total_consumo = df["consumo_kwh"].sum()
    total_custo = df["custo"].sum()

    return {
        "total_consumo": total_consumo,
        "total_custo": total_custo
    }