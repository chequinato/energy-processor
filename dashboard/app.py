
import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000"

st.title("⚡ Energy Dashboard")

# buscar dados da API
response = requests.get(f"{API_URL}/consumos")

if response.status_code == 200:
    data = response.json()
    df = pd.DataFrame(data)

    if not df.empty:
        st.subheader("📊 Dados")

        st.dataframe(df)

        # métricas
        st.subheader("⚡ Indicadores")

        total_consumo = df["consumo_kwh"].sum()
        total_custo = df["custo"].sum()

        col1, col2 = st.columns(2)

        col1.metric("Consumo Total (kWh)", total_consumo)
        col2.metric("Custo Total (R$)", total_custo)

        # gráfico
        st.subheader("📈 Consumo por Cliente")

        consumo_por_cliente = df.groupby("cliente")["consumo_kwh"].sum()

        st.bar_chart(consumo_por_cliente)

    else:
        st.warning("Nenhum dado encontrado")

else:
    st.error("Erro ao conectar com API")