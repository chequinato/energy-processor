# 📊 Regras de Negócio e Cálculos

## 🎯 Visão Geral

Este documento descreve todas as regras de negócio, cálculos e insights implementados no Energy Data Processor.

---

## 📋 Cálculos Principais

### 1. Cálculo de Custo
```python
# Fórmula principal
custo = consumo_kwh * preco_mwh / 1000

# Onde:
# - consumo_kwh: consumo em quilowatts-hora
# - preco_mwh: preço por megawatt-hora
# - Divisão por 1000: conversão de MWh para kWh
```

### 2. Cálculo de Eficiência
```python
# Custo por kWh (eficiência energética)
custo_por_kwh = custo_total / consumo_total

# Preço médio por MWh
preco_medio_mwh = media(preco_mwh)

# Consumo médio por cliente
consumo_medio_cliente = consumo_total / num_clientes
```

### 3. Análise de Variação Percentual
```python
# Variação mês a mês
variacao_percentual = ((consumo_atual - consumo_anterior) / consumo_anterior) * 100

# Aplicado quando:
# - Houver dados de pelo menos 2 meses
# - Consumo anterior > 0
```

---

## 🎯 Insights Automáticos

### 1. Análise de Crescimento
- **Crescimento elevado**: variação > +10%
- **Redução significativa**: variação < -10%
- **Alerta gerado**: automaticamente no dashboard

### 2. Concentração de Clientes
```python
# Top 3 clientes representam X% do custo
top3_percentual = (soma_top3 / custo_total) * 100

# Classificação:
# - > 60%: Alta concentração
# - 40-60%: Média concentração  
# - < 40%: Baixa concentração
```

### 3. Detecção de Anomalias
```python
# Método: Z-Score (2 desvios padrão)
limite_superior = media_cliente + 2 * std_cliente
is_anomalia = consumo_kwh > limite_superior

# Classificação:
# - Z > 2.5: Anomalia alta
# - 2.0 < Z ≤ 2.5: Anomalia moderada
# - Z ≤ 2.0: Normal
```

---

## 📊 Métricas e KPIs

### KPIs Principais
1. **Consumo Total**: Soma de todos consumos em kWh
2. **Custo Total**: Soma de todos custos em R$
3. **Preço Médio**: Custo médio por kWh
4. **Número de Clientes**: Clientes únicos no período

### KPIs Derivados
1. **Consumo Médio por Cliente**: `consumo_total / num_clientes`
2. **Custo Médio por Cliente**: `custo_total / num_clientes`
3. **Consumo Médio Mensal**: `consumo_total / meses_distintos`
4. **Crescimento Mensal**: Variação vs mês anterior

---

## 🎖️ Sistema de Rankings

### Rankings Implementados
1. **Rank de Consumo**: Maior consumidor (descendente)
2. **Rank de Custo**: Maior custo (descendente)
3. **Rank de Eficiência**: Menor custo/kWh (ascendente)

### Badges de Performance
```python
# Baseado em percentil
if percentile <= 20: return "🥇 Top 20%"
elif percentile <= 40: return "🥈 Top 40%"  
elif percentile <= 60: return "🥉 Médio"
else: return "⚠️ Abaixo"
```

---

## 📈 Análises Estatísticas

### Percentis Utilizados
- **P25**: 25º percentil (primeiro quartil)
- **P50 (Mediana)**: 50º percentil
- **P75**: 75º percentil (terceiro quartil)

### Análises de Distribuição
1. **Histograma**: Distribuição de consumo
2. **Box Plot**: Detecção de outliers por cliente
3. **Dispersão**: Consumo vs custo com eficiência

---

## 🎯 Metas e Recomendações

### Metas Sugeridas
1. **Meta de Consumo**: 10% abaixo da mediana
2. **Meta de Custo/kWh**: P25 atual (melhores 25%)
3. **Meta de Crescimento**: Manter < +10% mensal

### Recomendações Automáticas
1. **Clientes Caros**: Custo/kWh > P75
2. **Baixo Consumo**: Consumo < P25 (risco de churn)
3. **Alta Variação**: Variação > 30% (investigar)
4. **Oportunidade**: Economia potencial entre melhor/pior eficiência

---

## 🔍 Validações de Dados

### Validações Obrigatórias
1. **Colunas Obrigatórias**: cliente, consumo_kwh, preco_mwh
2. **Valores Nulos**: Não permitidos
3. **Valores Negativos**: Consumo e preço não podem ser negativos

### Tratamento de Dados
1. **Datas**: Conversão automática com `pd.to_datetime()`
2. **Números**: Normalização para float
3. **Clientela**: Criação automática de novos clientes

---

## 📊 Fórmulas de Benchmark

### Cálculos de Benchmark
```python
# Análise por cliente
df_benchmark = df.groupby('cliente').agg({
    'consumo_kwh': ['sum', 'mean', 'count'],
    'custo': ['sum', 'mean'],
    'preco_mwh': 'mean'
})

# Derivados
custo_por_kwh = custo_total / consumo_total
rank_consumo = consumo_total.rank(ascending=False)
rank_eficiencia = custo_por_kwh.rank()  # menor = melhor
```

### Comparações Relativas
1. **vs Mediana**: Acima/abaixo do consumo mediano
2. **vs Percentis**: Posição relativa (P25, P75)
3. **vs Período**: Variação temporal

---

## 🚨 Alertas e Notificações

### Tipos de Alerta
1. **Anomalias de Consumo**: Z-score > 2.0
2. **Crescimento Excessivo**: > +10% mensal
3. **Clientes de Risco**: Consumo < P25
4. **Ineficiência**: Custo/kWh > P75

### Prioridades
- **🔴 Alta**: Anomalias severas (Z > 2.5)
- **🟡 Média**: Variações moderadas
- **🟢 Baixa**: Informações de benchmark

---

## 📋 Fórmulas Resumo

### Cálculos Essenciais
```
Custo = Consumo_kWh × Preço_MWh ÷ 1000
Eficiência = Custo_Total ÷ Consumo_Total  
Variação% = ((Atual - Anterior) ÷ Anterior) × 100
Z-Score = (Valor - Média) ÷ Desvio_Padrão
```

### Métricas Chave
```
Consumo Médio/Cliente = Consumo_Total ÷ N_Clientes
Custo Médio/kWh = Custo_Total ÷ Consumo_Total
Participação% = (Cliente_Total ÷ Geral_Total) × 100
```

---

## 🔄 Processo de Atualização

1. **Upload**: Validação → Cálculo → Persistência
2. **Cache**: 5min dados brutos, 10min agregações
3. **Insights**: Recálculo automático a cada refresh
4. **Alertas**: Verificação em tempo real

---

## 📝 Observações Importantes

- **Precisão**: Todos cálculos com 2 casas decimais
- **Moeda**: Valores monetários em R$ (BRL)
- **Energia**: Consumos em kWh, preços em MWh
- **Períodos**: Análises mensais, trimestrais e anuais
- **Cache**: TTL configurável por tipo de dado

---

*Última atualização: 29/04/2026*
