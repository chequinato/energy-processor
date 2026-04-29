# 🏗️ Arquitetura do Sistema

## 🎯 Visão Geral

O Energy Data Processor segue uma arquitetura **microservices** com **backend API** e **frontend dashboard**, totalmente containerizada com Docker.

---

## 📊 Diagrama de Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend     │    │    Backend      │    │   Database      │
│  (Streamlit)   │◄──►│   (FastAPI)     │◄──►│   (SQLite)     │
│   Port: 8501   │    │   Port: 8000    │    │  energy.db      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Browser      │    │   Docker       │    │   File System  │
│  (Interface)   │    │  Compose       │    │   (Uploads)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 🔧 Backend (FastAPI)

### Estrutura de Pastas
```
backend/
├── app/
│   ├── controllers/     # Endpoints HTTP
│   ├── services/       # Lógica de negócio
│   ├── repositories/    # Acesso ao banco
│   ├── models/         # SQLAlchemy ORM
│   ├── schemas/        # Pydantic DTOs
│   ├── core/          # Configurações
│   └── utils/         # Helpers
├── main.py            # Entry point
├── Dockerfile
└── requirements.txt
```

### Componentes Principais

#### 1. Controllers (`app/controllers/`)
- **Responsabilidade**: Endpoints HTTP e validação de requisições
- **Arquivo principal**: `upload_controller.py`
- **Endpoints implementados**:
  - `POST /api/upload` - Upload e processamento de arquivos
  - `GET /api/consumos` - Listagem de consumos
  - `GET /api/clientes` - Lista de clientes únicos
  - `GET /api/relatorios` - Relatórios agregados
  - `GET /api/uploads` - Histórico de uploads
  - `DELETE /api/uploads/{id}` - Remover upload

#### 2. Services (`app/services/`)
- **Responsabilidade**: Lógica de negócio e orquestração
- **Arquivo principal**: `consumo_service.py`
- **Funções principais**:
  - `process_file()` - Orquestra validação, cálculo e persistência
  - `get_relatorios_service()` - Gera relatórios agregados

#### 3. Repositories (`app/repositories/`)
- **Responsabilidade**: Acesso direto ao banco de dados
- **Arquivos principais**:
  - `consumo_repository.py` - Operações de consumo
  - `cliente_repository.py` - Operações de cliente
- **Funções principais**:
  - `save_consumos()` - Persistência em lote
  - `get_relatorios()` - Consultas agregadas
  - `get_or_create_cliente()` - Upsert de clientes

#### 4. Models (`app/models/`)
- **Responsabilidade**: Definição de tabelas e relacionamentos
- **Arquivos principais**:
  - `consumo.py` - Modelo de dados de consumo
  - `cliente.py` - Modelo de clientes
  - `upload.py` - Modelo de histórico de uploads

#### 5. Utils (`app/utils/`)
- **Responsabilidade**: Funções utilitárias e regras
- **Arquivos principais**:
  - `validators.py` - Validações de dados
  - `calculations.py` - Cálculos de métricas
  - `file_reader.py` - Leitura de arquivos (CSV/Excel)

### Configuração e Database

#### Core (`app/core/`)
- **database.py**: Configuração SQLAlchemy e sessões
- **Engine**: SQLite com auto-commit
- **Session**: SessionLocal para injeção de dependência

#### Injeção de Dependências
```python
# Padrão FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Uso nos endpoints
@router.post("/upload")
async def upload_file(db: Session = Depends(get_db)):
    # lógica aqui
```

---

## 🎨 Frontend (Streamlit)

### Estrutura de Pastas
```
frontend/
└── dashboard/
    ├── app.py           # Aplicação principal
    ├── Dockerfile
    └── requirements.txt
```

### Componentes Principais

#### 1. Cache de Dados
```python
# Cache com TTL para performance
@st.cache_data(ttl=300)  # 5 minutos
def get_data():
    return requests.get(f"{API_URL}/consumos").json()

@st.cache_data(ttl=600)  # 10 minutos  
def get_uploads():
    return requests.get(f"{API_URL}/uploads").json()
```

#### 2. Estado da Sessão
```python
# Gerenciamento de estado
if "clientes" not in st.session_state:
    st.session_state.clientes = []

if "date_range" not in st.session_state:
    st.session_state.date_range = None
```

#### 3. Layout e Componentes
- **Sidebar**: Upload, filtros, ações
- **Métricas**: KPIs principais em cards
- **Gráficos**: 6 linhas com diferentes visualizações
- **Tabelas**: Dados detalhados com formatação

---

## 🗄️ Database (SQLite)

### Estrutura de Tabelas

#### 1. Clientes
```sql
CREATE TABLE clientes (
    id INTEGER PRIMARY KEY,
    nome VARCHAR UNIQUE NOT NULL,
    INDEX idx_nome (nome)
);
```

#### 2. Consumos
```sql
CREATE TABLE consumos (
    id INTEGER PRIMARY KEY,
    cliente_id INTEGER,
    consumo_kwh REAL,
    preco_mwh REAL,
    custo REAL,
    data DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES clientes (id),
    INDEX idx_cliente (cliente_id),
    INDEX idx_data (data)
);
```

#### 3. Uploads
```sql
CREATE TABLE uploads (
    id INTEGER PRIMARY KEY,
    filename VARCHAR,
    created_at DATETIME,
    INDEX idx_created (created_at)
);
```

### Relacionamentos
- **Cliente → Consumos**: One-to-Many
- **Upload**: Log independente para auditoria

---

## 🔄 Fluxo de Dados

### 1. Upload de Arquivo
```
Frontend (Streamlit)
    ↓ [POST multipart/form-data]
Backend (FastAPI)
    ↓ [validação]
Services (Business Logic)
    ↓ [cálculos]
Repositories (Database)
    ↓ [persistência]
SQLite Database
```

### 2. Consulta de Dados
```
Frontend (Streamlit)
    ↓ [HTTP GET]
Backend (FastAPI)
    ↓ [queries]
Repositories (Database)
    ↓ [SELECT]
SQLite Database
    ↓ [JSON response]
Frontend (Streamlit)
    ↓ [renderização]
Gráficos e Tabelas
```

### 3. Cache Strategy
```
Frontend Cache (Streamlit)
    ↓ [TTL: 5-10 min]
Backend Response (FastAPI)
    ↓ [query optimization]
Database Cache (SQLite)
    ↓ [file system]
energy.db
```

---

## 🔌 API Design

### Padrões REST
- **POST**: `/api/upload` - Criar recursos
- **GET**: `/api/consumos` - Listar recursos
- **GET**: `/api/clientes` - Listar recursos
- **GET**: `/api/relatorios` - Listar agregações
- **DELETE**: `/api/uploads/{id}` - Remover recurso

### Respostas Padrão
```python
# Sucesso
return {
    "filename": "dados.xlsx",
    "rows_processed": 150,
    "metrics": {"total_consumo": 15000, "total_custo": 1500}
}

# Erro
raise HTTPException(
    status_code=400,
    detail="Colunas obrigatórias faltando: ['cliente', 'consumo_kwh']"
)
```

### Validação
- **Pydantic**: Validação automática de tipos
- **Custom**: Validações de negócio nos utils
- **Database**: Constraints e índices

---

## 🚀 Performance e Cache

### Frontend Cache
```python
# Streamlit cache
@st.cache_data(ttl=300)  # Dados brutos
@st.cache_data(ttl=600)  # Agregações
@st.cache_data(ttl=1800) # Configurações
```

### Backend Optimization
- **Connection Pool**: SQLAlchemy session management
- **Batch Operations**: `add_all()` para múltiplos registros
- **Indexes**: Índices em colunas de consulta frequente
- **Lazy Loading**: Queries apenas quando necessário

### Database Optimization
```sql
-- Índices estratégicos
CREATE INDEX idx_consumos_cliente_data ON consumos(cliente_id, data);
CREATE INDEX idx_consumos_data ON consumos(data);
CREATE INDEX idx_clientes_nome ON clientes(nome);
```

---

## 🔒 Segurança

### CORS Configuration
```python
# FastAPI CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # Streamlit
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Input Validation
- **File Types**: Apenas CSV/Excel
- **File Size**: Limite configurável
- **Data Validation**: Valores não negativos
- **SQL Injection**: Proteção via SQLAlchemy

---

## 📝 Logging e Monitoramento

### Backend Logging
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Processando arquivo: %s", filename)
logger.error("Erro na validação: %s", str(error))
```

### Frontend Error Handling
```python
try:
    response = requests.post(f"{API_URL}/upload", files=files)
    if response.ok:
        st.success("Arquivo processado!")
    else:
        st.error(f"Erro: {response.text}")
except Exception as e:
    st.error(f"Erro de conexão: {str(e)}")
```

---

## 🔄 Escalabilidade

### Horizontal Scaling
- **Frontend**: Múltiplas instâncias Streamlit
- **Backend**: Load balancer + múltiplos containers FastAPI
- **Database**: PostgreSQL para produção (substituir SQLite)

### Vertical Scaling
- **CPU**: Mais cores para processamento paralelo
- **Memory**: Mais RAM para cache e grandes datasets
- **Storage**: SSD para performance do SQLite

---

## 📊 Tecnologias e Versões

### Backend Stack
- **FastAPI**: 0.104.1+ (API moderna)
- **SQLAlchemy**: 2.0.23+ (ORM)
- **Pydantic**: 2.5.0+ (Validação)
- **Uvicorn**: Servidor ASGI
- **Pandas**: 2.1.3+ (Processamento)

### Frontend Stack  
- **Streamlit**: 1.28.1+ (Dashboard)
- **Plotly**: 5.17.0+ (Gráficos)
- **Requests**: HTTP client
- **ReportLab**: 4.0.7+ (PDF)

### Database
- **SQLite**: 3.x (Desenvolvimento)
- **PostgreSQL**: Recomendado para produção

---

## 🚀 Deploy Considerations

### Development
- **Docker Compose**: Orquestração local
- **Volume Mount**: Persistência de dados
- **Port Mapping**: 8000 (API), 8501 (Frontend)

### Production
- **Kubernetes**: Orquestração em nuvem
- **Load Balancer**: Distribuição de tráfego
- **Managed Database**: PostgreSQL/RDS
- **CDN**: Cache estático
- **Monitoring**: Prometheus + Grafana

---

## 📋 Próximos Passos Arquiteturais

1. **Database Migration**: SQLite → PostgreSQL
2. **Message Queue**: Redis/Celery para async processing
3. **API Gateway**: Kong/AWS API Gateway
4. **Service Mesh**: Istio para microservices
5. **Event Sourcing**: Kafka para eventos de domínio

---

*Última atualização: 29/04/2026*
