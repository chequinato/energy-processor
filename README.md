# ⚡ Energy Data Processor

Sistema para processamento e análise de consumo de energia com API + Dashboard.

## 🚀 Funcionalidades

- Upload de arquivos CSV/Excel (com validação de formato, tamanho e conteúdo)
- Processamento e validação de dados
- Cálculo de consumo e custo
- API REST com FastAPI (com cache opcional em Redis)
- Dashboard interativo com Streamlit
- Geração de relatórios (PDF) e insights com IA

## 🏗️ Arquitetura

- **Backend:** FastAPI + SQLAlchemy 2
- **Frontend:** Streamlit + Plotly
- **Banco:** SQLite
- **Cache:** Redis (opcional: sem ele a API funciona, só sem cache)
- **Infra:** Docker Compose + GitHub Actions

## ▶️ Como rodar

### Com Docker (recomendado)

```bash
cp .env.example .env   # opcional: preencha OPENAI_API_KEY
docker compose up --build
```

Acessos:

- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health
- Dashboard: http://localhost:8501

### Sem Docker

```bash
# backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# frontend (em outro terminal)
pip install -r frontend/dashboard/requirements.txt
API_URL=http://localhost:8000/api streamlit run frontend/dashboard/app.py
```

## ⚙️ Configuração

As variáveis ficam em `.env` (veja `.env.example`):

| Variável | Padrão | Descrição |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./energy.db` | Conexão do banco |
| `REDIS_URL` | `redis://redis:6379/0` | Cache dos relatórios |
| `CACHE_TTL_SECONDS` | `60` | Tempo de vida do cache |
| `CORS_ORIGINS` | `["http://localhost:8501"]` | Origens permitidas |
| `UPLOAD_DIR` | `data/uploads` | Onde guardar cópia dos arquivos |
| `MAX_UPLOAD_SIZE_MB` | `10` | Tamanho máximo do upload |
| `API_URL` | `http://backend:8000/api` | URL da API usada pelo dashboard |

## 📡 Endpoints

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/api/upload` | Envia um CSV/XLSX (`cliente`, `consumo_kwh`, `preco_mwh`, `data` opcional) |
| `GET` | `/api/consumos` | Lista consumos (filtros: `cliente`, `data_inicio`, `data_fim`) |
| `GET` | `/api/clientes` | Lista clientes |
| `GET` | `/api/relatorios` | Totais e média por cliente |
| `GET` | `/api/relatorios/resumo` | Totais gerais |
| `GET` | `/api/uploads` | Histórico de uploads |
| `DELETE` | `/api/uploads/{id}` | Remove o upload e os consumos importados por ele |
| `GET` | `/health` | Status da API, banco e cache |

Exemplo:

```bash
curl -F file=@arquivo.xlsx http://localhost:8000/api/upload
```

## 🧪 Testes

```bash
cd backend
pip install -r requirements-dev.txt
ruff check .
pytest
```

O CI roda lint e testes a cada push/PR e depois sobe o Docker Compose aguardando os health checks.

## 📁 Estrutura

```
backend/     # API FastAPI (app/, tests/)
frontend/    # Dashboard Streamlit
data/        # uploads
docs/        # documentação completa
```

## 📚 Documentação completa

👉 Veja em: [docs/projeto-completo.md](docs/projeto-completo.md)

## 🔮 Melhorias futuras

- Autenticação JWT
- PostgreSQL + migrações com Alembic
- Testes do dashboard
