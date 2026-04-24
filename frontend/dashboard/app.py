import streamlit as st
import requests
import pandas as pd
import plotly.express as px

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

API_URL = "http://backend:8000/api"

# -------------------------------
# 📄 GERAR PDF
# -------------------------------
def gerar_pdf(df):
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet
    from io import BytesIO
    import plotly.express as px

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    elementos = []

    # -------------------------------
    # 🧾 TÍTULO
    # -------------------------------
    elementos.append(Paragraph("📊 Relatório de Consumo de Energia", styles["Title"]))
    elementos.append(Spacer(1, 16))

    total_consumo = df["consumo_kwh"].sum()
    total_custo = df["custo"].sum()

    elementos.append(Paragraph(f"<b>Consumo total:</b> {total_consumo:.0f} kWh", styles["Normal"]))
    elementos.append(Paragraph(f"<b>Custo total:</b> R$ {total_custo:.2f}", styles["Normal"]))

    elementos.append(Spacer(1, 20))

    # -------------------------------
    # 📈 CONSUMO POR CLIENTE
    # -------------------------------
    elementos.append(Paragraph("📈 Consumo por Cliente", styles["Heading2"]))
    elementos.append(Spacer(1, 10))

    consumo_cliente = (
        df.groupby("cliente")["consumo_kwh"]
        .sum()
        .reset_index()
        .sort_values(by="consumo_kwh", ascending=False)
    )

    fig_bar = px.bar(consumo_cliente, x="cliente", y="consumo_kwh")

    img1 = BytesIO()
    fig_bar.write_image(img1, format="png")
    img1.seek(0)

    elementos.append(Image(img1, width=450, height=260))
    elementos.append(Spacer(1, 20))

    # -------------------------------
    # 📉 TENDÊNCIA
    # -------------------------------
    elementos.append(Paragraph("📉 Tendência de Consumo", styles["Heading2"]))
    elementos.append(Spacer(1, 10))

    df_trend = df.copy()
    df_trend["mes"] = df_trend["data"].dt.to_period("M").dt.to_timestamp()

    df_trend = (
        df_trend.groupby("mes")["consumo_kwh"]
        .sum()
        .reset_index()
    )

    fig_line = px.line(df_trend, x="mes", y="consumo_kwh", markers=True)

    img2 = BytesIO()
    fig_line.write_image(img2, format="png")
    img2.seek(0)

    elementos.append(Image(img2, width=450, height=260))
    elementos.append(Spacer(1, 20))

    # -------------------------------
    # 💰 CUSTO POR MÊS (NOVO 🔥)
    # -------------------------------
    elementos.append(Paragraph("💰 Custo por mês", styles["Heading2"]))
    elementos.append(Spacer(1, 10))

    df_custo = df.copy()
    df_custo["mes"] = df_custo["data"].dt.to_period("M").dt.to_timestamp()

    df_custo = (
        df_custo.groupby("mes")["custo"]
        .sum()
        .reset_index()
    )

    fig_custo = px.line(df_custo, x="mes", y="custo", markers=True)

    img3 = BytesIO()
    fig_custo.write_image(img3, format="png")
    img3.seek(0)

    elementos.append(Image(img3, width=450, height=260))
    elementos.append(Spacer(1, 20))

    # -------------------------------
    # 🏆 TOP CLIENTES
    # -------------------------------
    elementos.append(Paragraph("🏆 Top 5 clientes", styles["Heading2"]))
    elementos.append(Spacer(1, 10))

    top_clientes = (
        df.groupby("cliente")["consumo_kwh"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
    )

    for cliente, consumo in top_clientes.items():
        elementos.append(Paragraph(f"{cliente}: {consumo:.0f} kWh", styles["Normal"]))

    # -------------------------------
    # FINALIZA
    # -------------------------------
    doc.build(elementos)

    buffer.seek(0)
    return buffer


# -------------------------------
# ⚙️ CONFIG
# -------------------------------
st.set_page_config(
    page_title="Energy Dashboard",
    layout="wide"
)

st.title("⚡ Energy Dashboard")

# -------------------------------
# 🔎 SIDEBAR (UPLOAD + FILTROS)
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

            if response.ok:
                st.success("Processado com sucesso!")
            else:
                st.error("Erro ao enviar arquivo")

    st.divider()

    if st.button("🔄 Atualizar dados"):
        st.cache_data.clear()
        st.rerun()

    if st.button("🧹 Limpar filtros"):
        st.session_state.clear()
        st.rerun()


# -------------------------------
# 📁 HISTÓRICO DE UPLOADS
# -------------------------------
st.divider()
st.header("📁 Histórico de Uploads")

@st.cache_data
def get_uploads():
    response = requests.get(f"{API_URL}/uploads")
    if response.ok:
        return response.json()
    return []

uploads = get_uploads()

if uploads:
    for u in uploads:
        col1, col2 = st.columns([3, 1])

        with col1:
            st.caption(f"📄 {u['filename']}")
            st.caption(f"🕒 {u['created_at']}")

        with col2:
            if st.button("🗑️", key=f"del_{u['id']}"):
                requests.delete(f"{API_URL}/uploads/{u['id']}")
                st.cache_data.clear()
                st.rerun()
else:
    st.caption("Nenhum upload ainda.")


# -------------------------------
# 📡 BUSCAR DADOS
# -------------------------------
@st.cache_data
def get_data():
    response = requests.get(f"{API_URL}/consumos")
    if response.ok:
        return pd.DataFrame(response.json())
    return pd.DataFrame()

df = get_data()

# -------------------------------
# 📊 EXIBIÇÃO
# -------------------------------
if not df.empty:

    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    df = df.dropna(subset=["data"])

    # -------------------------------
    # 🔎 FILTROS
    # -------------------------------
    with st.sidebar:
        st.header("🔎 Filtros")

        clientes = df["cliente"].dropna().unique()

        clientes_selecionados = st.multiselect(
            "Clientes",
            options=clientes,
            default=clientes,
            key="clientes"
        )

        datas = st.date_input(
            "Período",
            value=(df["data"].min(), df["data"].max()),
            key="date_range"
        )

        if isinstance(datas, tuple) and len(datas) == 2:
            data_inicio, data_fim = datas
        else:
            data_inicio, data_fim = None, None

        min_consumo = float(df["consumo_kwh"].min())
        max_consumo = float(df["consumo_kwh"].max())

        faixa_consumo = st.slider(
            "Faixa de Consumo (kWh)",
            min_value=min_consumo,
            max_value=max_consumo,
            value=(min_consumo, max_consumo),
            key="faixa_consumo"
        )

    # -------------------------------
    # 🔥 FILTRAGEM
    # -------------------------------
    df_filtrado = df.copy()

    df_filtrado = df_filtrado[
        df_filtrado["cliente"].isin(clientes_selecionados)
    ]

    if data_inicio and data_fim:
        df_filtrado = df_filtrado[
            (df_filtrado["data"] >= pd.to_datetime(data_inicio)) &
            (df_filtrado["data"] <= pd.to_datetime(data_fim))
        ]

    df_filtrado = df_filtrado[
        (df_filtrado["consumo_kwh"] >= faixa_consumo[0]) &
        (df_filtrado["consumo_kwh"] <= faixa_consumo[1])
    ]

    if df_filtrado.empty:
        st.warning("Nenhum dado encontrado com esses filtros.")
        st.stop()

    # -------------------------------
    # ⚡ MÉTRICAS
    # -------------------------------
    total_consumo = df_filtrado["consumo_kwh"].sum()
    total_custo = df_filtrado["custo"].sum()

    col1, col2 = st.columns(2)

    col1.metric("⚡ Consumo Total", f"{total_consumo:.0f} kWh")
    col2.metric("💰 Custo Total", f"R$ {total_custo:.2f}")

    st.caption(f"{len(df_filtrado)} registros encontrados")

    st.divider()

    # -------------------------------
    # 📄 PDF
    # -------------------------------
    pdf = gerar_pdf(df_filtrado)

    st.download_button(
        label="📄 Baixar relatório PDF",
        data=pdf,
        file_name="relatorio_energia.pdf",
        mime="application/pdf"
    )

    st.divider()

    # -------------------------------
    # 📊 GRÁFICOS
    # -------------------------------

    # 🔹 LINHA 1
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Consumo por Cliente")

        consumo_cliente = (
            df_filtrado
            .groupby("cliente")["consumo_kwh"]
            .sum()
            .reset_index()
            .sort_values(by="consumo_kwh", ascending=False)
        )

        fig_bar = px.bar(consumo_cliente, x="cliente", y="consumo_kwh")
        st.plotly_chart(fig_bar, width="stretch")

    with col2:
        st.subheader("🏆 Top Clientes")

        top_clientes = consumo_cliente.head(5)

        fig_top = px.bar(
            top_clientes,
            x="consumo_kwh",
            y="cliente",
            orientation="h"
        )

        st.plotly_chart(fig_top, width="stretch")

    st.divider()

    # 🔹 LINHA 2
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📉 Tendência de Consumo")

        df_trend = df_filtrado.copy()
        df_trend["mes"] = df_trend["data"].dt.to_period("M").dt.to_timestamp()

        df_trend = (
            df_trend
            .groupby("mes")["consumo_kwh"]
            .sum()
            .reset_index()
        )

        fig_line = px.line(df_trend, x="mes", y="consumo_kwh", markers=True)
        st.plotly_chart(fig_line, width="stretch")

    with col2:
        st.subheader("💰 Custo por mês")

        df_custo = df_filtrado.copy()
        df_custo["mes"] = df_custo["data"].dt.to_period("M").dt.to_timestamp()

        df_custo = (
            df_custo
            .groupby("mes")["custo"]
            .sum()
            .reset_index()
        )

        fig_custo = px.line(df_custo, x="mes", y="custo", markers=True)
        st.plotly_chart(fig_custo, width="stretch")

    # -------------------------------
    # 📋 TABELA
    # -------------------------------
    st.divider()
    st.subheader("📋 Dados")
    st.dataframe(df_filtrado, use_container_width=True)

else:
    st.warning("Nenhum dado disponível. Faça upload de um arquivo.")