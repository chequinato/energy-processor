import streamlit as st
import requests
import pandas as pd
import plotly.express as px  # 🔥 NOVO

API_URL = "http://127.0.0.1:8000/api"

# 🔥 NOVO — config da página
st.set_page_config(
    page_title="Energy Dashboard",
    layout="wide"
)

st.title("⚡ Energy Dashboard")

# -------------------------------
# 🔎 SIDEBAR (FILTROS + UPLOAD)
# -------------------------------
with st.sidebar:
    st.header("📤 Upload")

    uploaded_file = st.file_uploader(
        "CSV ou Excel",
        type=["csv", "xlsx"]
    )

    if uploaded_file is not None:
        if st.button("📤 Processar arquivo"):
            with st.spinner("Processando..."):
                response = requests.post(
                    f"{API_URL}/upload",
                    files={"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                )

            if response.ok:  # 🔧 ALTERADO (melhor que status_code == 200)
                st.success("Processado com sucesso!")
            else:
                st.error("Erro ao enviar arquivo")

    st.divider()  # 🔥 NOVO

    if st.button("🔄 Atualizar dados"):
        st.cache_data.clear()
        st.rerun()

# -------------------------------
# 📡 BUSCAR DADOS (CACHE)
# -------------------------------
@st.cache_data
def get_data():
    response = requests.get(f"{API_URL}/consumos")
    if response.ok:  # 🔧 ALTERADO
        return pd.DataFrame(response.json())
    return pd.DataFrame()

df = get_data()

# -------------------------------
# 📊 EXIBIÇÃO
# -------------------------------
if not df.empty:

    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    df = df.dropna(subset=["data"])

    with st.sidebar:
        st.header("🔎 Filtros")

        clientes = df["cliente"].dropna().unique()
        cliente_selecionado = st.selectbox("Cliente", ["Todos"] + list(clientes))

        datas = st.date_input(
            "Período",
            value=(df["data"].min(), df["data"].max())
        )

    # 🔥 tratamento correto
    if isinstance(datas, tuple) and len(datas) == 2:
        data_inicio, data_fim = datas
    else:
        data_inicio, data_fim = None, None

    # 🔥 AGORA sim fora do else
    df_filtrado = df.copy()

    if cliente_selecionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado["cliente"] == cliente_selecionado]

    if data_inicio is not None and data_fim is not None:
        df_filtrado = df_filtrado[
            (df_filtrado["data"] >= pd.to_datetime(data_inicio)) &
            (df_filtrado["data"] <= pd.to_datetime(data_fim))
        ]

    # -------------------------------
    # ⚡ MÉTRICAS (NO TOPO)
    # -------------------------------
    total_consumo = df_filtrado["consumo_kwh"].sum()
    total_custo = df_filtrado["custo"].sum()

    col1, col2 = st.columns(2)

    col1.metric("⚡ Consumo Total", f"{total_consumo:.0f} kWh")  # 🔧 ALTERADO
    col2.metric("💰 Custo Total", f"R$ {total_custo:.2f}")       # 🔧 ALTERADO

    st.divider()  # 🔥 NOVO

    # -------------------------------
    # 📊 GRÁFICOS (PLOTLY)
    # -------------------------------
    col1, col2 = st.columns(2)

    # 📈 Consumo por cliente
    with col1:
        st.subheader("📈 Consumo por Cliente")

        consumo_cliente = (
            df_filtrado
            .groupby("cliente")["consumo_kwh"]
            .sum()
            .reset_index()
        )

        fig_bar = px.bar(
            consumo_cliente,
            x="cliente",
            y="consumo_kwh",
            title="Consumo por Cliente"
        )

        st.plotly_chart(fig_bar, use_container_width=True)  # 🔥 NOVO

    # 📉 Tendência
    with col2:
        st.subheader("📉 Tendência de Consumo")

        df_trend = df_filtrado.copy()
        df_trend["mes"] = df_trend["data"].dt.to_period("M").dt.to_timestamp()

        df_trend = (
            df_trend
            .groupby("mes")["consumo_kwh"]
            .sum()
            .reset_index()
        )

        fig_line = px.line(
            df_trend,
            x="mes",
            y="consumo_kwh",
            markers=True,
            title="Consumo ao longo do tempo"
        )

        st.plotly_chart(fig_line, use_container_width=True)  # 🔥 NOVO

    st.divider()  # 🔥 NOVO

    # -------------------------------
    # 📋 TABELA (NO FINAL)
    # -------------------------------
    st.subheader("📋 Dados")

    st.dataframe(
        df_filtrado,
        use_container_width=True
    )

else:
    st.warning("Nenhum dado disponível. Faça upload de um arquivo.")