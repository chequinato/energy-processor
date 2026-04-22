# ⚡ Energy Data Processor + API + Dashboard

## 🧠 Visão do Sistema
Upload arquivo → Processa/Valida/Calcula → Salva SQLite → API REST + Dashboard Streamlit

## 📦 Estrutura
```
energy-processor/
├── app/                 # FastAPI Backend
│   ├── controllers/     # Endpoints
│   ├── services/        # Business logic
│   ├── repositories/    # DB access
│   ├── models/          # SQLAlchemy
│   ├── schemas/         # Pydantic DTOs
│   ├── core/            # Config/DB
│   └── utils/           # Helpers (file, validate, calc)
├── dashboard/           # Streamlit Frontend
├── data/uploads/        # Arquivos Excel/CSV
├── scripts/             # Seed DB
├── requirements.txt
├── .env.example         # Copie para .env
└── README.md
```

## 🚀 Setup & Run

1. **Instalar dependências**
```
pip install -r requirements.txt
```

2. **Configurar .env** (copie .env.example)
```
cp .env.example .env
```

3. **Recriar DB** (deleta dados antigos)
```
rm energy.db  # optional
uvicorn app.main:app --reload
```
(cria tables auto)

4. **Seed dados de exemplo**
```
python scripts/seed.py
```

5. **Rodar API**
```
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

6. **Rodar Dashboard**
```
streamlit run dashboard/app.py
```

## 🔌 API Endpoints (http://127.0.0.1:8000/api)
- `POST /upload` - Upload Excel/CSV (valida/processa/salva)
- `GET /consumos` - Lista consumos + clientes
- `GET /clientes` - Lista clientes únicos
- `GET /relatorios` - Agregados por cliente (total/media)
- `GET /relatorios/resumo` - Totais gerais

## 📊 Funcionalidades
- **Upload**: CSV/Excel → valida cols/tipos/negativos → calcula custo → salva
- **Dashboard**: Filtros cliente/data, métricas, gráficos (bar/line trends)
- **Relatórios**: GROUP BY cliente, totais/médias
- **Logging**: Service layer

## 🧪 Teste Rápido
1. API rodando + seed.py
2. Dashboard: upload teste.xlsx → see charts/filtros
3. API: curl -F file=@data/uploads/planilha_consumos.xlsx http://127.0.0.1:8000/api/upload

## 🔧 Stack
FastAPI | SQLAlchemy | Pandas | Streamlit | SQLite | Pydantic

Feito! Projeto lapidado conforme spec. 🎉
