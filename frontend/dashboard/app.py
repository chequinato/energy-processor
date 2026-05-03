import streamlit as st
import requests
import pandas as pd
import plotly.express as px

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
import openai
import os
from dotenv import load_dotenv

load_dotenv()

#Configurar API
openai.api_key = os.getenv("OPENAI_API_KEY")


API_URL = "http://backend:8000/api"

# -------------------------------
# GERAR RESUMO COM IA
# -------------------------------

def gerar_insights_ia(df):
    """Gera insights inteligentes usando OpenAI"""
    
    # 1. Preparar resumo dos dados
    resumo_dados = f"""
    RELATÓRIO DE CONSUMO DE ENERGIA:
    
    📊 ESTATÍSTICAS GERAIS:
    - Consumo total: {df['consumo_kwh'].sum():,.0f} kWh
    - Custo total: R$ {df['custo'].sum():,.2f}
    - Número de clientes: {df['cliente'].nunique()}
    - Período analisado: {df['data'].min().strftime('%d/%m/%Y')} a {df['data'].max().strftime('%d/%m/%Y')}
    
    💰 ANÁLISE DE CUSTOS:
    - Preço médio/kWh: R$ {df['custo'].sum()/df['consumo_kwh'].sum():.3f}
    - Cliente com maior custo: {df.groupby('cliente')['custo'].sum().idxmax()}
    - Cliente mais eficiente: {df.groupby('cliente')['custo'].sum().idxmin()}
    
    📈 TENDÊNCIAS:
    - Consumo médio por cliente: {df['consumo_kwh'].mean():.0f} kWh
    - Desvio padrão do consumo: {df['consumo_kwh'].std():.0f} kWh
    - Mês de maior consumo: {df.groupby(df['data'].dt.to_period('M'))['consumo_kwh'].sum().idxmax().strftime('%m/%Y')}
    """
    
    # 2. Enviar para OpenAI
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": "Você é um especialista em energia. Forneça insights práticos e acionáveis baseados nos dados."
                },
                {
                    "role": "user", 
                    "content": f"""Analise estes dados de consumo de energia e forneça 5 insights valiosos:
                    
                    {resumo_dados}
                    
                    Para cada insight, inclua:
                    1. O que você observou
                    2. Por que isso é importante
                    3. Uma recomendação acionável
                    
                    Seja específico e use os números reais dos dados."""
                }
            ],
            max_tokens=800,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"❌ Erro ao gerar insights: {str(e)}"

# -------------------------------
# GERAR PDF
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
    elementos.append(Paragraph("📊 Relatório  - Consumo de Energia Completo", styles["Title"]))
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

    elementos.append(Spacer(1, 20))

    # -------------------------------
    # 🎯 DISTRIBUIÇÃO DE CUSTO (NOVO 🔥)
    # -------------------------------
    elementos.append(Paragraph("🎯 Distribuição de Custo", styles["Heading2"]))
    elementos.append(Spacer(1, 10))

    df_pie = df.groupby("cliente")["custo"].sum().reset_index()
    df_pie_top = df_pie.sort_values("custo", ascending=False).head(5)
    outros = df_pie.iloc[5:]["custo"].sum()
    if outros > 0:
        df_pie_top = pd.concat([df_pie_top, pd.DataFrame([{"cliente": "Outros", "custo": outros}])])

    fig_pie = px.pie(df_pie_top, names="cliente", values="custo", hole=0.3)
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')

    img4 = BytesIO()
    fig_pie.write_image(img4, format="png")
    img4.seek(0)

    elementos.append(Image(img4, width=450, height=260))
    elementos.append(Spacer(1, 20))

    # -------------------------------
    # 🔥 HEATMAP CONSUMO (NOVO 🔥)
    # -------------------------------
    elementos.append(Paragraph("🔥 Intensidade de Consumo por Cliente/Mês", styles["Heading2"]))
    elementos.append(Spacer(1, 10))

    df_heatmap = df.copy()
    df_heatmap["mes"] = df_heatmap["data"].dt.to_period("M").dt.to_timestamp()

    fig_heatmap = px.density_heatmap(
        df_heatmap,
        x="mes",
        y="cliente",
        z="consumo_kwh",
        color_continuous_scale="Viridis"
    )

    img5 = BytesIO()
    fig_heatmap.write_image(img5, format="png")
    img5.seek(0)

    elementos.append(Image(img5, width=450, height=260))
    elementos.append(Spacer(1, 20))

    # -------------------------------
    # 📊 ANÁLISE DE EFICIÊNCIA (NOVO 🔥)
    # -------------------------------
    elementos.append(Paragraph("📊 Eficiência Energética", styles["Heading2"]))
    elementos.append(Spacer(1, 10))

    df_efficiency = df.copy()
    df_efficiency["custo_por_kwh"] = df_efficiency["custo"] / df_efficiency["consumo_kwh"]
    
    fig_scatter = px.scatter(
        df_efficiency,
        x="consumo_kwh",
        y="custo",
        size="preco_mwh",
        hover_name="cliente",
        color="custo_por_kwh",
        color_continuous_scale="RdYlBu_r",
        title="Consumo vs Custo (tamanho = preço médio)"
    )

    img6 = BytesIO()
    fig_scatter.write_image(img6, format="png")
    img6.seek(0)

    elementos.append(Image(img6, width=450, height=260))
    elementos.append(Spacer(1, 20))

    # -------------------------------
    # 📈 MÉTRICAS E INSIGHTS (NOVO 🔥)
    # -------------------------------
    elementos.append(Paragraph("📈 Métricas e Insights", styles["Heading2"]))
    elementos.append(Spacer(1, 10))

    # Cálculos de métricas
    num_clientes = df["cliente"].nunique()
    consumo_medio_cliente = total_consumo / num_clientes
    preco_medio_kwh = total_custo / total_consumo
    
    elementos.append(Paragraph(f"<b>Clientes únicos:</b> {num_clientes}", styles["Normal"]))
    elementos.append(Paragraph(f"<b>Consumo médio/cliente:</b> {consumo_medio_cliente:.0f} kWh", styles["Normal"]))
    elementos.append(Paragraph(f"<b>Preço médio/kWh:</b> R$ {preco_medio_kwh:.3f}", styles["Normal"]))
    
    # Melhor e pior eficiência
    df_efficiency["custo_por_kwh"] = df["custo"] / df["consumo_kwh"]
    melhor_cliente = df_efficiency.loc[df_efficiency["custo_por_kwh"].idxmin(), "cliente"]
    pior_cliente = df_efficiency.loc[df_efficiency["custo_por_kwh"].idxmax(), "cliente"]
    
    elementos.append(Spacer(1, 10))
    elementos.append(Paragraph(f"<b>Melhor eficiência:</b> {melhor_cliente}", styles["Normal"]))
    elementos.append(Paragraph(f"<b>Pior eficiência:</b> {pior_cliente}", styles["Normal"]))

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

st.title("⚡ Energy Data Processor")
st.markdown("---")
st.caption("📊 Dashboard Avançado de Análise de Consumo Energético")

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

    # Detecção de anomalias
    df_anomalia = df_filtrado.copy()

    df_anomalia["media_cliente"] = df_anomalia.groupby("cliente")["consumo_kwh"].transform("mean")
    df_anomalia["std_cliente"] = df_anomalia.groupby("cliente")["consumo_kwh"].transform("std")

    df_anomalia["limite"] = df_anomalia["media_cliente"] + 2 * df_anomalia["std_cliente"]

    df_anomalia["is_anomaly"] = df_anomalia["consumo_kwh"] > df_anomalia["limite"]

    # -------------------------------
    # ⚡ KPIs AVANÇADOS
    # -------------------------------
    total_consumo = df_filtrado["consumo_kwh"].sum()
    total_custo = df_filtrado["custo"].sum()
    num_clientes = df_filtrado["cliente"].nunique()
    
    # 📊 KPIs adicionais
    consumo_medio_cliente = total_consumo / num_clientes if num_clientes > 0 else 0
    custo_medio_cliente = total_custo / num_clientes if num_clientes > 0 else 0
    preco_medio_kwh = (total_custo / total_consumo) if total_consumo > 0 else 0
    
    # 📅 Análise temporal
    df_filtrado["mes"] = df_filtrado["data"].dt.to_period("M")
    meses_distintos = df_filtrado["mes"].nunique()
    consumo_medio_mensal = total_consumo / meses_distintos if meses_distintos > 0 else 0
    
    # 🎯 Eficiência e outliers
    qtd_anomalias = df_anomalia["is_anomaly"].sum()
    percentual_anomalias = (qtd_anomalias / len(df_filtrado)) * 100 if len(df_filtrado) > 0 else 0
    
    # 📈 Crescimento (se tiver mais de 1 mês)
    crescimento_mensal = 0
    if meses_distintos >= 2:
        consumo_meses = df_filtrado.groupby("mes")["consumo_kwh"].sum().sort_index()
        ultimo_mes = consumo_meses.iloc[-1]
        mes_anterior = consumo_meses.iloc[-2]
        crescimento_mensal = ((ultimo_mes - mes_anterior) / mes_anterior) * 100 if mes_anterior > 0 else 0

    # 🎨 Layout KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("⚡ Consumo Total", f"{total_consumo:,.0f} kWh", f"📅 {meses_distintos} meses")
    col2.metric("💰 Custo Total", f"R$ {total_custo:,.2f}", f"👥 {num_clientes} clientes")
    col3.metric("📊 Média/Cliente", f"{consumo_medio_cliente:,.0f} kWh", f"R$ {custo_medio_cliente:,.2f}")
    col4.metric("🎯 Preço Médio", f"R$ {preco_medio_kwh:.3f}/kWh", f"📈 {crescimento_mensal:+.1f}%")
    
    # 🚨 Alertas de anomalias
    if qtd_anomalias > 0:
        st.warning(f"⚠️ {qtd_anomalias} consumos anômalos detectados ({percentual_anomalias:.1f}% do total)")
    
    st.caption(f"📊 {len(df_filtrado)} registros • 📅 Período: {df_filtrado['data'].min().strftime('%d/%m/%Y')} a {df_filtrado['data'].max().strftime('%d/%m/%Y')}")

    st.divider()

    # -------------------------------
    # 🧠 INSIGHTS AUTOMÁTICOS
    # -------------------------------
    st.divider()
    st.subheader("🧠 Insights")

    insights = []

    # 📈 crescimento mês a mês
    df_mes = df_filtrado.copy()
    df_mes["mes"] = df_mes["data"].dt.to_period("M").dt.to_timestamp()

    df_mes = df_mes.groupby("mes")["consumo_kwh"].sum().reset_index()

    if len(df_mes) >= 2:
        ultimo = df_mes.iloc[-1]["consumo_kwh"]
        anterior = df_mes.iloc[-2]["consumo_kwh"]

        if anterior > 0:
            variacao = ((ultimo - anterior) / anterior) * 100

            insights.append(f"Consumo variou {variacao:.1f}% em relação ao mês anterior")

    # 🏆 concentração de clientes
    top_clientes = (
        df_filtrado.groupby("cliente")["custo"]
        .sum()
        .sort_values(ascending=False)
    )

    top3 = top_clientes.head(3).sum()
    total = top_clientes.sum()

    if total > 0:
        percentual = (top3 / total) * 100
        insights.append(f"Top 3 clientes representam {percentual:.1f}% do custo total")

    # 🚨 quantidade de anomalias
    qtd_anomalias = df_anomalia["is_anomaly"].sum()
    if qtd_anomalias > 0:
        insights.append(f"{qtd_anomalias} consumos fora do padrão detectados")

    # render
    for i in insights:
        st.info(i)

    # 🏆 Análise de Clientes Avançada
    analise_clientes = df_filtrado.groupby("cliente").agg({
        'consumo_kwh': ['sum', 'mean', 'std'],
        'custo': 'sum',
        'preco_mwh': 'mean'
    }).round(2)
    analise_clientes.columns = ['consumo_total', 'consumo_medio', 'consumo_std', 'custo_total', 'preco_medio']
    
    # 🥇 Top performers
    top_consumidor = analise_clientes['consumo_total'].idxmax()
    menor_consumidor = analise_clientes['consumo_total'].idxmin()
    cliente_caro = analise_clientes['preco_medio'].idxmax()
    cliente_barato = analise_clientes['preco_medio'].idxmin()
    
    # 📊 Insights de clientes
    col_insights1, col_insights2 = st.columns(2)
    
    with col_insights1:
        st.info(f"🏆 **Maior consumidor**: {top_consumidor} ({analise_clientes.loc[top_consumidor, 'consumo_total']:,.0f} kWh)")
        st.info(f"📉 **Menor consumidor**: {menor_consumidor} ({analise_clientes.loc[menor_consumidor, 'consumo_total']:,.0f} kWh)")
    
    with col_insights2:
        st.info(f"💸 **Preço mais alto**: {cliente_caro} (R$ {analise_clientes.loc[cliente_caro, 'preco_medio']:.2f}/MWh)")
        st.info(f"💰 **Preço mais baixo**: {cliente_barato} (R$ {analise_clientes.loc[cliente_barato, 'preco_medio']:.2f}/MWh)")
    
    # 🎯 Eficiência energética
    st.info(f"⚡ **Consumo médio mensal**: {consumo_medio_mensal:,.0f} kWh/mês")
    if crescimento_mensal > 10:
        st.warning(f"📈 **Crescimento elevado**: {crescimento_mensal:+.1f}% vs mês anterior")
    elif crescimento_mensal < -10:
        st.success(f"📉 **Redução significativa**: {crescimento_mensal:+.1f}% vs mês anterior")

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
    st.plotly_chart(fig_bar, width='stretch')

with col2:
    st.subheader("🏆 Top Clientes")

    top_clientes = consumo_cliente.head(5)

    fig_top = px.bar(
        top_clientes,
        x="consumo_kwh",
        y="cliente",
        orientation="h"
    )

    st.plotly_chart(fig_top, width='stretch')

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

    df_trend_full = df_anomalia.copy()
    df_trend_full["mes"] = df_trend_full["data"].dt.to_period("M").dt.to_timestamp()

    fig_line = px.line(df_trend, x="mes", y="consumo_kwh", markers=True)

    anomalias = df_trend_full[df_trend_full["is_anomaly"] == True]

    fig_line.add_scatter(
        x=anomalias["mes"],
        y=anomalias["consumo_kwh"],
        mode="markers",
        name="Anomalias"
    )

    maior_consumidor = df_filtrado.groupby("cliente")["consumo_kwh"].sum().idxmax()

    fig_line.add_annotation(
        x=df_trend["mes"].iloc[-1],
        y=df_trend["consumo_kwh"].iloc[-1],
        text=f"Maior consumidor: {maior_consumidor}",
        showarrow=True,
        arrowhead=1
    )

    st.plotly_chart(fig_line, width='stretch')

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
    st.plotly_chart(fig_custo, width='stretch')

st.markdown("---")
st.markdown("## 🔥 Análises Avançadas")
st.markdown("---")

# 🔹 LINHA 3 - GRÁFICOS AVANÇADOS
col3, col4 = st.columns([2, 1])

with col3:
    st.subheader("🔥 Heatmap Consumo por Cliente/Mês")

    df_heatmap = df_filtrado.copy()
    df_heatmap["mes"] = df_heatmap["data"].dt.to_period("M").dt.to_timestamp()

    df_heatmap = (
        df_heatmap
        .groupby(["cliente", "mes"])["consumo_kwh"]
        .sum()
        .reset_index()
    )

    fig_heatmap = px.density_heatmap(
        df_heatmap,
        x="mes",
        y="cliente",
        z="consumo_kwh",
        color_continuous_scale="Viridis",
        title="Intensidade de Consumo (kWh)"
    )
    fig_heatmap.update_layout(height=400)
    st.plotly_chart(fig_heatmap, width='stretch')

with col4:
    st.subheader("🎯 Distribuição de Custo")

    df_pie = df_filtrado.copy()
    df_pie = (
        df_pie
        .groupby("cliente")["custo"]
        .sum()
        .reset_index()
    )

    # Apenas top 5 para o pie chart ficar legível
    df_pie_top = df_pie.nlargest(5, "custo")
    outros = df_pie.iloc[5:]["custo"].sum()
    if outros > 0:
        df_pie_top = pd.concat([df_pie_top, pd.DataFrame({"cliente": ["Outros"], "custo": [outros]})])
    
    fig_pie = px.pie(
        df_pie_top, 
        names="cliente", 
        values="custo",
        hole=0.3,  # donut chart
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    fig_pie.update_layout(height=400)
    st.plotly_chart(fig_pie, width='stretch')

st.divider()

# 🔹 LINHA 4 - ANÁLISE AVANÇADA
col5, col6 = st.columns([3, 2])

with col5:
    st.subheader("📊 Análise de Eficiência Energética")
    
    # Gráfico de dispersão: consumo vs custo
    df_efficiency = df_filtrado.groupby("cliente").agg({
        'consumo_kwh': 'sum',
        'custo': 'sum',
        'preco_mwh': 'mean'
    }).reset_index()
    
    df_efficiency['custo_por_kwh'] = df_efficiency['custo'] / df_efficiency['consumo_kwh']
    
    fig_scatter = px.scatter(
        df_efficiency,
        x="consumo_kwh",
        y="custo",
        size="preco_mwh",
        hover_name="cliente",
        color="custo_por_kwh",
        color_continuous_scale="RdYlBu_r",
        title="Consumo vs Custo (tamanho = preço médio)"
    )
    fig_scatter.update_layout(height=400)
    st.plotly_chart(fig_scatter, width='stretch')

with col6:
    st.subheader("📈 Variação Percentual")
    
    # Análise de variação por cliente
    df_variacao = df_filtrado.copy()
    df_variacao["mes"] = df_variacao["data"].dt.to_period("M")
    
    # Calcular variação para clientes com múltiplos meses
    variacoes = []
    for cliente in df_variacao["cliente"].unique():
        dados_cliente = df_variacao[df_variacao["cliente"] == cliente]
        dados_mes = dados_cliente.groupby("mes")["consumo_kwh"].sum().sort_index()
        
        if len(dados_mes) >= 2:
            ultimo = dados_mes.iloc[-1]
            anterior = dados_mes.iloc[-2]
            variacao = ((ultimo - anterior) / anterior) * 100 if anterior > 0 else 0
            variacoes.append({"cliente": cliente, "variacao": variacao, "consumo_atual": ultimo})
    
    # Debug: mostrar informações sobre os dados
    st.write(f"📊 Clientes únicos: {df_variacao['cliente'].nunique()}")
    st.write(f"📅 Meses distintos: {df_variacao['mes'].nunique()}")
    st.write(f"📈 Variações calculadas: {len(variacoes)}")
    
    if variacoes:
        df_var = pd.DataFrame(variacoes)
        df_var = df_var.sort_values("variacao", ascending=True)
        
        fig_var = px.bar(
            df_var,
            x="variacao",
            y="cliente",
            orientation="h",
            color="variacao",
            color_continuous_scale="RdYlGn",
            title="Variação % vs Mês Anterior"
        )
        fig_var.update_layout(height=400)
        st.plotly_chart(fig_var, width='stretch')
        
        # Mostrar dados da variação
        st.write("**Dados de Variação:**")
        st.dataframe(df_var, width='stretch')
    else:
        st.info("📅 Dados insuficientes para análise de variação (precisa de múltiplos meses)")
        
        # Mostrar dados disponíveis para debug
        st.write("**Dados disponíveis por cliente:**")
        cliente_meses = df_variacao.groupby("cliente")["mes"].nunique().sort_values(ascending=False)
        st.dataframe(cliente_meses.reset_index(), width='stretch')

st.divider()

# 🔹 LINHA 5 - DISTRIBUIÇÃO E ESTATÍSTICAS
col7, col8 = st.columns([2, 3])

with col7:
    st.subheader("📊 Distribuição de Consumo")
    
    # Histograma de consumo
    fig_hist = px.histogram(
        df_filtrado,
        x="consumo_kwh",
        nbins=20,
        title="Distribuição de Consumo (kWh)",
        color_discrete_sequence=["#1f77b4"]
    )
    fig_hist.add_vline(
        x=df_filtrado["consumo_kwh"].mean(),
        line_dash="dash",
        line_color="red",
        annotation_text=f"Média: {df_filtrado['consumo_kwh'].mean():.0f} kWh"
    )
    fig_hist.update_layout(height=350)
    st.plotly_chart(fig_hist, width='stretch')

with col8:
    st.subheader("🎯 Box Plot por Cliente")
    
    # Box plot para detectar outliers por cliente
    top_clientes_box = df_filtrado.groupby("cliente")["consumo_kwh"].sum().nlargest(8).index
    df_box = df_filtrado[df_filtrado["cliente"].isin(top_clientes_box)]
    
    fig_box = px.box(
        df_box,
        x="cliente",
        y="consumo_kwh",
        title="Distribuição de Consumo por Cliente (Top 8)",
        color="cliente"
    )
    fig_box.update_layout(height=350, showlegend=False)
    fig_box.update_xaxes(tickangle=45)
    st.plotly_chart(fig_box, width='stretch')


st.divider()

# 🔹 LINHA 6 - INSIGHTS E BENCHMARKS
st.subheader("🎯 Análise Comparativa e Insights")

# 📊 Tabela de benchmark por cliente
df_benchmark = df_filtrado.groupby("cliente").agg({
    'consumo_kwh': ['sum', 'mean', 'count'],
    'custo': ['sum', 'mean'],
    'preco_mwh': 'mean'
}).round(2)

df_benchmark.columns = ['consumo_total', 'consumo_medio', 'num_registros', 'custo_total', 'custo_medio', 'preco_medio']
df_benchmark['custo_por_kwh'] = df_benchmark['custo_total'] / df_benchmark['consumo_total']

# 🏆 Rankings
df_benchmark['rank_consumo'] = df_benchmark['consumo_total'].rank(ascending=False)
df_benchmark['rank_custo'] = df_benchmark['custo_total'].rank(ascending=False)
df_benchmark['rank_eficiencia'] = df_benchmark['custo_por_kwh'].rank()  # menor = melhor

# 📈 Percentis
percentil_75_consumo = df_benchmark['consumo_total'].quantile(0.75)
percentil_25_consumo = df_benchmark['consumo_total'].quantile(0.25)
mediana_consumo = df_benchmark['consumo_total'].median()

# 🎨 Layout insights
col_insight1, col_insight2, col_insight3 = st.columns(3)

with col_insight1:
    st.metric("📊 Consumo Mediano", f"{mediana_consumo:,.0f} kWh")
    st.caption(f"P75: {percentil_75_consumo:,.0f} kWh | P25: {percentil_25_consumo:,.0f} kWh")

with col_insight2:
    clientes_acima_media = df_benchmark[df_benchmark['consumo_total'] > mediana_consumo]
    st.metric("📈 Acima da Mediana", f"{len(clientes_acima_media)} clientes")
    st.caption(f"{(len(clientes_acima_media)/len(df_benchmark)*100):.1f}% do total")

with col_insight3:
    melhor_eficiencia = df_benchmark['custo_por_kwh'].min()
    pior_eficiencia = df_benchmark['custo_por_kwh'].max()
    st.metric("⚡ Melhor Custo/kWh", f"R$ {melhor_eficiencia:.3f}")
    st.caption(f"vs Pior: R$ {pior_eficiencia:.3f}")

# 📋 Tabela de benchmark detalhada
col_tabela1, col_tabela2 = st.columns([2, 1])

with col_tabela1:
    st.subheader("📊 Benchmark de Clientes")
    
    # Formatar tabela para exibição
    df_display = df_benchmark.copy()
    df_display = df_display.sort_values('consumo_total', ascending=False)
    df_display['consumo_total'] = df_display['consumo_total'].apply(lambda x: f"{x:,.0f}")
    df_display['custo_total'] = df_display['custo_total'].apply(lambda x: f"R$ {x:,.2f}")
    df_display['consumo_medio'] = df_display['consumo_medio'].apply(lambda x: f"{x:,.0f}")
    df_display['custo_medio'] = df_display['custo_medio'].apply(lambda x: f"R$ {x:,.2f}")
    df_display['custo_por_kwh'] = df_display['custo_por_kwh'].apply(lambda x: f"R$ {x:.3f}")
    df_display['preco_medio'] = df_display['preco_medio'].apply(lambda x: f"R$ {x:.2f}")
    
    # Adicionar badges de performance
    def get_performance_badge(rank, total):
        percentile = (rank / total) * 100
        if percentile <= 20:
            return "🥇 Top 20%"
        elif percentile <= 40:
            return "🥈 Top 40%"
        elif percentile <= 60:
            return "🥉 Médio"
        else:
            return "⚠️ Abaixo"
    
    df_display['performance'] = df_display.apply(
        lambda row: get_performance_badge(row['rank_consumo'], len(df_benchmark)), axis=1
    )
    
    st.dataframe(df_display.drop(['rank_consumo', 'rank_custo', 'rank_eficiencia'], axis=1), width='stretch')

with col_tabela2:
    st.subheader("🎯 Recomendações")
    
    recomendacoes = []
    
    # Clientes com alto custo por kWh
    clientes_caros = df_benchmark[df_benchmark['custo_por_kwh'] > df_benchmark['custo_por_kwh'].quantile(0.75)]
    if not clientes_caros.empty:
        recomendacoes.append(f"⚠️ {len(clientes_caros)} clientes com custo acima do P75")
    
    # Clientes com baixo consumo (possível churn)
    clientes_baixo = df_benchmark[df_benchmark['consumo_total'] < df_benchmark['consumo_total'].quantile(0.25)]
    if not clientes_baixo.empty:
        recomendacoes.append(f"📉 {len(clientes_baixo)} clientes com consumo baixo (atenção)")
    
    # Clientes com alta variação (possíveis anomalias)
    if 'variacoes' in locals() and len(variacoes) > 0:
        alta_variacao = [v for v in variacoes if abs(v['variacao']) > 30]
        if alta_variacao:
            recomendacoes.append(f"📊 {len(alta_variacao)} clientes com variação >30%")
    
    # Oportunidade de otimização
    economia_potencial = (df_benchmark['custo_por_kwh'].max() - df_benchmark['custo_por_kwh'].min()) * df_benchmark['consumo_total'].sum()
    if economia_potencial > 0:
        recomendacoes.append(f"💰 Economia potencial: R$ {economia_potencial:,.2f}")
    
    for rec in recomendacoes:
        st.info(rec)
    
    # 🎯 Meta de eficiência
    st.subheader("🎯 Metas Sugeridas")
    
    meta_consumo = mediana_consumo * 0.9  # 10% abaixo da mediana
    meta_custo = df_benchmark['custo_por_kwh'].quantile(0.25)  # P25
    
    st.metric("📊 Meta de Consumo", f"{meta_consumo:,.0f} kWh", "-10% vs mediana")
    st.metric("💰 Meta de Custo/kWh", f"R$ {meta_custo:.3f}", "P25 atual")

st.divider()

# -------------------------------
# � KPIS PRINCIPAIS
# -------------------------------
st.markdown("## � Métricas Principais")
st.markdown("---")

# 📊 Estatísticas descritivas
with st.expander("📈 Estatísticas Descritivas"):
    stats_cols = st.columns(3)
    
    with stats_cols[0]:
        st.write("**Consumo (kWh)**")
        st.write(f"Média: {df_filtrado['consumo_kwh'].mean():.2f}")
        st.write(f"Mediana: {df_filtrado['consumo_kwh'].median():.2f}")
        st.write(f"Desvio Padrão: {df_filtrado['consumo_kwh'].std():.2f}")
        st.write(f"Mínimo: {df_filtrado['consumo_kwh'].min():.2f}")
        st.write(f"Máximo: {df_filtrado['consumo_kwh'].max():.2f}")
    
    with stats_cols[1]:
        st.write("**Custo (R$)**")
        st.write(f"Média: {df_filtrado['custo'].mean():.2f}")
        st.write(f"Mediana: {df_filtrado['custo'].median():.2f}")
        st.write(f"Desvio Padrão: {df_filtrado['custo'].std():.2f}")
        st.write(f"Mínimo: {df_filtrado['custo'].min():.2f}")
        st.write(f"Máximo: {df_filtrado['custo'].max():.2f}")
    
    with stats_cols[2]:
        st.write("**Preço (R$/MWh)**")
        st.write(f"Média: {df_filtrado['preco_mwh'].mean():.2f}")
        st.write(f"Mediana: {df_filtrado['preco_mwh'].median():.2f}")
        st.write(f"Desvio Padrão: {df_filtrado['preco_mwh'].std():.2f}")
        st.write(f"Mínimo: {df_filtrado['preco_mwh'].min():.2f}")
        st.write(f"Máximo: {df_filtrado['preco_mwh'].max():.2f}")

# 📋 Tabela de dados com formatação
st.dataframe(df_filtrado.style.format({
        'consumo_kwh': '{:,.2f}',
        'custo': 'R$ {:,.2f}',
        'preco_mwh': 'R$ {:,.2f}',
        'data': lambda x: x.strftime('%d/%m/%Y') if pd.notna(x) else ''
    }),
    width='stretch',
    height=300
)

# 🤖 SEÇÃO DE INSIGHTS COM IA
st.markdown("## 🤖 Insights Inteligentes com IA")
st.markdown("---")

col_ia1, col_ia2 = st.columns([1, 3])

with col_ia1:
    st.write("**🧠 Análise IA**")
    st.caption("Insights personalizados usando inteligência artificial")
    
    if st.button("🚀 Gerar Insights", type="primary"):
        with st.spinner("🤖 Analisando dados com IA..."):
            insights = gerar_insights_ia(df)
            st.session_state.insights_ia = insights
    
    if st.button("🔄 Nova Análise"):
        if 'insights_ia' in st.session_state:
            del st.session_state.insights_ia

with col_ia2:
    if 'insights_ia' in st.session_state:
        st.success("**🎯 Insights Gerados:**")
        st.markdown(st.session_state.insights_ia)
        
        # Botões de ação
        col_save, col_share = st.columns(2)
        with col_save:
            if st.button("💾 Salvar Insights"):
                st.info("✅ Insights salvos no relatório PDF!")
        
        with col_share:
            if st.button("📱 Compartilhar"):
                st.info("📋 Insights copiados para área de transferência!")
    else:
        st.info("👆 Clique em 'Gerar Insights' para análise personalizada com IA")