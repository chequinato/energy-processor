import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000"

st.title("⚡ Energy Dashboard")

# -------------------------------
# 📤 UPLOAD
# -------------------------------
uploaded_file = st.file_uploader("Faça upload do arquivo CSV ou Excel", type=["csv", "xlsx"])

if uploaded_file is not None:
    if st.button("📤 Processar arquivo"):
        with st.spinner("Processando arquivo..."):
            response = requests.post(
                f"{API_URL}/upload",
                files={"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
            )

        if response.status_code == 200:
            st.success("Arquivo enviado e processado com sucesso!")
        else:
            st.error("Erro ao enviar arquivo")

# -------------------------------
# 🔄 ATUALIZAR
# -------------------------------
if st.button("🔄 Atualizar dados"):
    st.cache_data.clear()
    st.rerun()

# -------------------------------
# 📡 BUSCAR DADOS (CACHE)
# -------------------------------
@st.cache_data
def get_data():
    response = requests.get(f"{API_URL}/consumos")
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    return pd.DataFrame()

df = get_data()

# -------------------------------
# 📊 EXIBIÇÃO
# -------------------------------
if not df.empty:

    # -------------------------------
    # 🔎 FILTROS
    # -------------------------------
    st.subheader("🔎 Filtros")

    clientes = df["cliente"].unique()
    cliente_selecionado = st.selectbox("Cliente", ["Todos"] + list(clientes))

    df_filtrado = df.copy()

    if cliente_selecionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado["cliente"] == cliente_selecionado]

    # -------------------------------
    # 📋 TABELA
    # -------------------------------
    st.subheader("📊 Dados")
    st.dataframe(df_filtrado, use_container_width=True)

    # -------------------------------
    # ⚡ MÉTRICAS
    # -------------------------------
    st.subheader("⚡ Indicadores")

    total_consumo = df_filtrado["consumo_kwh"].sum()
    total_custo = df_filtrado["custo"].sum()

    col1, col2 = st.columns(2)

    col1.metric("Consumo Total (kWh)", f"{total_consumo:.2f}")
    col2.metric("Custo Total (R$)", f"{total_custo:.2f}")

    # -------------------------------
    # 📈 GRÁFICO
    # -------------------------------
    st.subheader("📈 Consumo por Cliente")

    consumo_por_cliente = df_filtrado.groupby("cliente")["consumo_kwh"].sum()

    st.bar_chart(consumo_por_cliente)

else:
    st.warning("Nenhum dado encontrado 😢")