# 📚 Documentação Completa - Energy Data Processor

## 🎯 Visão Geral do Projeto

O **Energy Data Processor** é um sistema completo para processamento de dados de consumo de energia, composto por:
- **API REST** (FastAPI) para backend
- **Dashboard** (Streamlit) para visualização
- **Docker** para containerização
- **SQLite** para persistência

**Fluxo principal**: Upload de arquivo → Processamento/Validação → Cálculos → Armazenamento → API + Dashboard

---

## 🏗️ Arquitetura do Sistema

### Estrutura de Diretórios
```
energy-processor/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── controllers/        # Endpoints HTTP
│   │   ├── services/          # Lógica de negócio
│   │   ├── repositories/       # Acesso ao banco
│   │   ├── models/            # SQLAlchemy ORM
│   │   ├── schemas/           # Pydantic DTOs
│   │   ├── core/              # Configurações/DB
│   │   └── utils/             # Helpers (validação, cálculos)
│   ├── main.py                # Entry point FastAPI
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   └── dashboard/
│       ├── app.py             # Streamlit Dashboard
│       ├── Dockerfile
│       └── requirements.txt
├── data/uploads/               # Arquivos Excel/CSV
├── scripts/                    # Seed e utilitários
├── docs/                       # Documentação
├── docker-compose.yml
├── energy.db                   # SQLite DB
└── requirements.txt
```

---

## 🐳 Docker e Containerização

### Docker Compose
```yaml
version: "3.9"
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./energy.db:/app/energy.db
      - ./data:/app/data
  
  frontend:
    build: ./frontend/dashboard
    ports:
      - "8501:8501"
    depends_on:
      - backend
```

### Dockerfiles

#### Backend (Python 3.11)
```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Frontend (Python 3.11 + Chrome)
```dockerfile
FROM python:3.11-slim-bookworm
WORKDIR /app
# Instala dependências do sistema + Chrome para PDF
RUN apt-get update && apt-get install -y \
    wget gnupg ca-certificates libnss3 libatk-bridge2.0-0 \
    libcups2 libxcomposite1 libxdamage1 libxfixes3 \
    libxrandr2 libgbm1 libxkbcommon0 libpango-1.0-0 \
    libcairo2 libasound2 fonts-liberation \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/google.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google.list \
    && apt-get update && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Comandos Docker Principais
```bash
# Build e iniciar todos os serviços
docker-compose up --build

# Iniciar em background
docker-compose up -d

# Parar serviços
docker-compose down

# Ver logs
docker-compose logs -f
docker-compose logs backend
docker-compose logs frontend

# Reconstruir apenas um serviço
docker-compose up --build backend
```

---

## 🐍 Tecnologias e Bibliotecas Python

### Backend Stack
- **FastAPI**: Framework web moderno para APIs
- **SQLAlchemy**: ORM para banco de dados
- **Pydantic**: Validação de dados e serialização
- **Pandas**: Manipulação de dados
- **Uvicorn**: Servidor ASGI
- **SQLite**: Banco de dados relacional

### Frontend Stack
- **Streamlit**: Framework para dashboards
- **Plotly**: Visualização de gráficos
- **ReportLab**: Geração de PDFs
- **Requests**: Cliente HTTP

### Bibliotecas Principais (requirements.txt)
```
fastapi>=0.104.1
uvicorn[standard]>=0.24.0
sqlalchemy>=2.0.23
pydantic>=2.5.0
pandas>=2.1.3
python-multipart>=0.0.6
streamlit>=1.28.1
plotly>=5.17.0
reportlab>=4.0.7
requests>=2.31.0
```

---

## 🗄️ Modelo de Dados (SQLAlchemy)

### Tabelas

#### Cliente
```python
class Cliente(Base):
    __tablename__ = "clientes"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, unique=True, index=True)
```

#### Consumo
```python
class Consumo(Base):
    __tablename__ = "consumos"
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    consumo_kwh = Column(Float)
    preco_mwh = Column(Float)
    custo = Column(Float)
    data = Column(DateTime, server_default=func.now())
```

#### Upload
```python
class Upload(Base):
    __tablename__ = "uploads"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    created_at = Column(DateTime)
```

---

## 🔌 API REST Endpoints

### Upload e Processamento
- `POST /api/upload` - Upload de arquivo Excel/CSV
- `GET /api/uploads` - Listar uploads
- `DELETE /api/uploads/{upload_id}` - Deletar upload

### Consultas
- `GET /api/consumos` - Lista todos consumos com clientes
- `GET /api/clientes` - Lista clientes únicos
- `GET /api/relatorios` - Relatórios agregados por cliente
- `GET /api/relatorios/resumo` - Totais gerais do sistema

### Exemplo de Uso
```bash
# Upload de arquivo
curl -F file=@planilha.xlsx http://localhost:8000/api/upload

# Listar consumos
curl http://localhost:8000/api/consumos

# Relatórios
curl http://localhost:8000/api/relatorios
```

---

## ⚙️ Funcionalidades e Métodos

### 1. Upload e Processamento de Arquivos

#### Controllers (`upload_controller.py`)
```python
@router.post("/upload")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Salva arquivo temporariamente
    # Processa com pandas
    # Valida dados
    # Calcula métricas
    # Salva no banco
```

#### Services (`consumo_service.py`)
```python
def process_file(db, df):
    validate_columns(df)      # Valida colunas obrigatórias
    validate_data(df)         # Valida valores (não negativos)
    metrics = calculate_metrics(df)  # Calcula custos
    save_consumos(db, df)     # Persiste no banco
    return metrics
```

### 2. Validação de Dados

#### Validators (`validators.py`)
```python
def validate_columns(df):
    required = ["cliente", "consumo_kwh", "preco_mwh"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Colunas faltando: {missing}")

def validate_data(df):
    if df.isnull().any().any():
        raise ValueError("Existem valores nulos")
    if (df["consumo_kwh"] < 0).any():
        raise ValueError("Consumo não pode ser negativo")
```

### 3. Cálculos

#### Calculations (`calculations.py`)
```python
def calculate_metrics(df):
    df["custo"] = df["consumo_kwh"] * df["preco_mwh"] / 1000
    total_consumo = int(df["consumo_kwh"].sum())
    total_custo = float(df["custo"].sum())
    return {"total_consumo": total_consumo, "total_custo": total_custo}
```

### 4. Leitura de Arquivos

#### File Reader (`file_reader.py`)
```python
def read_file(file_path: str) -> pd.DataFrame:
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    elif file_path.endswith('.xlsx'):
        df = pd.read_excel(file_path)
    else:
        raise ValueError("Use CSV ou XLSX")
    
    # Tratamento de data
    if "data" in df.columns:
        df["data"] = pd.to_datetime(df["data"], errors="coerce", dayfirst=True)
    
    return df
```

---

## 📊 Streamlit Dashboard

### Funcionalidades Principais
- **Upload de arquivos** via interface
- **Filtros** por cliente e período
- **Gráficos** interativos (bar, line, pie)
- **Métricas** em tempo real
- **Exportação** PDF de relatórios

### Componentes
```python
# Sidebar com filtros
st.sidebar.header("🔍 Filtros")
clientes = get_clientes()
cliente_selected = st.sidebar.selectbox("Cliente", ["Todos"] + clientes)

# Métricas principais
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Consumo", f"{total_consumo:,.0f} kWh")
with col2:
    st.metric("Custo Total", f"R$ {total_custo:,.2f}")

# Gráficos Plotly
fig = px.bar(df_grouped, x="cliente", y="consumo_kwh", title="Consumo por Cliente")
st.plotly_chart(fig, use_container_width=True)

# Geração de PDF
if st.button("📄 Gerar PDF Relatório"):
    pdf_data = gerar_pdf(df_processado)
    st.download_button("Baixar PDF", pdf_data, "relatorio.pdf")
```

---

## 🗃️ Repositories (Acesso a Dados)

### Consumo Repository
```python
def save_consumos(db: Session, df: pd.DataFrame):
    objetos = []
    for _, row in df.iterrows():
        cliente = get_or_create_cliente(db, row["cliente"])
        consumo = Consumo(
            cliente_id=cliente.id,
            consumo_kwh=float(row["consumo_kwh"]),
            preco_mwh=float(row["preco_mwh"]),
            custo=float(row["custo"]),
            data=row.get("data")
        )
        objetos.append(consumo)
    
    db.add_all(objetos)
    db.commit()

def get_relatorios(db: Session):
    results = db.query(
        Cliente.nome,
        func.sum(Consumo.consumo_kwh).label("total_consumo"),
        func.sum(Consumo.custo).label("total_custo"),
        func.avg(Consumo.consumo_kwh).label("media_consumo"),
    ).join(Consumo).group_by(Cliente.id).all()
    
    return [{"cliente": nome, "total_consumo": total, ...} 
            for nome, total, custo, media in results]
```

## ⚡ Cache com Redis

O projeto utiliza **Redis** para otimizar a performance dos endpoints de relatórios.

### 🔹 Como funciona

- Os endpoints abaixo são cacheados:
  - `/api/relatorios`
  - `/api/relatorios/resumo`

- Na primeira requisição:
  - Os dados são calculados no backend
  - Armazenados no Redis (TTL: 60s)

- Nas próximas requisições:
  - Os dados são retornados diretamente do cache (mais rápido ⚡)

### 🔄 Invalidação de Cache

O cache é automaticamente limpo quando:

- Um novo arquivo é enviado (`POST /api/upload`)
- Um upload é removido (`DELETE /api/uploads/{id}`)

### 🐳 Redis no Docker

O Redis roda como um serviço no `docker-compose`:

```yaml
redis:
  image: redis:7
  ports:
    - "6379:6379"
---

## 🧪 Conceitos Python Utilizados

### 1. Type Hints
```python
from typing import List, Optional
def process_file(db: Session, df: pd.DataFrame) -> dict:
    pass
```

### 2. DataClasses vs Pydantic Models
```python
# Pydantic para validação
from pydantic import BaseModel
class ConsumoCreate(BaseModel):
    cliente: str
    consumo_kwh: float
    preco_mwh: float
```

### 3. Context Managers
```python
# Session do SQLAlchemy
from sqlalchemy.orm import Session
db = SessionLocal()
try:
    # operações
    db.commit()
finally:
    db.close()
```

### 4. List Comprehensions
```python
clientes = [c[0] for c in clientes]
resultados = [{"cliente": nome, "total": total} for nome, total in results]
```

### 5. Error Handling
```python
try:
    df = read_file(file_path)
    process_file(db, df)
except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))
except Exception as e:
    db.rollback()
    raise HTTPException(status_code=500, detail="Erro interno")
```

### 6. Decoradores
```python
# FastAPI decorators
@router.post("/upload")
@router.get("/consumos")
async def upload_file(file: UploadFile = File(...)):
    pass
```

### 7. Async/Await
```python
async def upload_file(file: UploadFile = File(...)):
    file_content = await file.read()
    with open(file_path, "wb") as f:
        f.write(file_content)
```

---

## 🗄️ SQL Utilizado

### Criação de Tabelas (Automaticamente via SQLAlchemy)
```sql
-- Clientes
CREATE TABLE clientes (
    id INTEGER PRIMARY KEY,
    nome VARCHAR UNIQUE NOT NULL
);

-- Consumos  
CREATE TABLE consumos (
    id INTEGER PRIMARY KEY,
    cliente_id INTEGER,
    consumo_kwh REAL,
    preco_mwh REAL,
    custo REAL,
    data DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES clientes (id)
);

-- Uploads
CREATE TABLE uploads (
    id INTEGER PRIMARY KEY,
    filename VARCHAR,
    created_at DATETIME
);
```

### Queries Principais
```sql
-- Relatório por cliente
SELECT 
    c.nome,
    SUM(co.consumo_kwh) as total_consumo,
    SUM(co.custo) as total_custo,
    AVG(co.consumo_kwh) as media_consumo
FROM clientes c
JOIN consumos co ON c.id = co.cliente_id
GROUP BY c.id, c.nome;

-- Listagem completa
SELECT c.nome, co.consumo_kwh, co.preco_mwh, co.custo, co.data
FROM consumos co
JOIN clientes c ON co.cliente_id = c.id;

-- Clientes únicos
SELECT DISTINCT nome FROM clientes ORDER BY nome;
```

---

## 🚀 Setup e Execução

### 1. Ambiente Local
```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar ambiente
cp .env.example .env

# Iniciar API
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Iniciar Dashboard (outro terminal)
streamlit run frontend/dashboard/app.py --server.port 8501
```

### 2. Docker (Produção)
```bash
# Build e iniciar
docker-compose up --build

# Acessar serviços
# API: http://localhost:8000
# Dashboard: http://localhost:8501
# Docs API: http://localhost:8000/docs
```

### 3. Seed de Dados
```bash
# Popular banco com dados de exemplo
python scripts/seed.py

# Ou via Docker
docker-compose exec backend python scripts/seed.py
```

---

## 📋 Fluxo Completo de Funcionamento

### 1. Upload do Arquivo
1. Usuário seleciona arquivo Excel/CSV no dashboard
2. Arquivo enviado para `POST /api/upload`
3. Arquivo salvo temporariamente em `data/uploads/`

### 2. Processamento
1. **Leitura**: Pandas lê CSV/Excel
2. **Validação**: Verifica colunas obrigatórias, valores nulos, negativos
3. **Cálculo**: `custo = consumo_kwh * preco_mwh / 1000`
4. **Persistência**: Salva clientes e consumos no SQLite

### 3. Visualização
1. Dashboard consulta `GET /api/consumos` e `GET /api/relatorios`
2. Dados filtrados por cliente/período
3. Gráficos gerados com Plotly
4. PDF gerado com ReportLab

### 4. Relatórios
- **Por cliente**: Total consumo, custo total, média
- **Geral**: Soma de todos clientes
- **Tendências**: Evolução temporal (se houver data)

---

## 🔧 Configuração

### Variáveis de Ambiente (.env)
```bash
DATABASE_URL=sqlite:///./energy.db
UVICORN_HOST=127.0.0.1
UVICORN_PORT=8000
LOG_LEVEL=INFO
```

### Configuração FastAPI
```python
app = FastAPI(title="Energy Processor API", version="1.0.0")

# CORS para Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🐛 Debug e Monitoramento

### Logs
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Iniciando processamento do arquivo")
logger.error(f"Erro ao processar: {str(e)}")
```

### Testes Manuais
```bash
# Teste API
curl -X POST -F "file=@teste.xlsx" http://localhost:8000/api/upload

# Ver banco SQLite
sqlite3 energy.db
.tables
SELECT * FROM consumos LIMIT 5;
```

---

## 📚 Conceitos Avançados Python

### 1. ORM com SQLAlchemy
```python
# Models definem estrutura do banco
# Queries tipadas com Session
# Relacionamentos automaticos
```

### 2. Injeção de Dependências (FastAPI)
```python
# Depends(get_db) injere sessão do banco
# Automaticamente gerencia ciclo de vida
```

### 3. Serialização (Pydantic)
```python
# Validação automática de dados
# Conversão de tipos
# Documentação da API
```

### 4. Processamento de Dados (Pandas)
```python
# DataFrames para manipulação
# GroupBy para agregações
# Merge/Join para combinar dados
```

### 5. Async Programming
```python
# async/await para I/O operations
# Não bloqueia servidor durante upload
```

---

## 🔮 Próximos Passos e Melhorias

### Sugestões de Evolução
1. **Autenticação**: JWT para proteger endpoints
2. **Cache**: Redis para consultas frequentes
3. **Background Jobs**: Celery para processamento assíncrono
4. **Testes**: Pytest com cobertura
5. **Monitoramento**: Prometheus + Grafana
6. **CI/CD**: GitHub Actions para deploy
7. **Banco**: PostgreSQL para produção
8. **Frontend**: React/Vue para mobile

### Escalabilidade
- **Horizontal**: Múltiplas instâncias do backend
- **Vertical**: Aumentar recursos dos containers
- **Database**: Partitioning por data/cliente

---

## 📞 Contato e Suporte

Este documento cobre todos os aspectos técnicos do projeto Energy Data Processor. Para dúvidas específicas, consulte:

1. **Código fonte**: Disponível nos arquivos do projeto
2. **API Docs**: `http://localhost:8000/docs` (Swagger)
3. **Logs**: Ver logs do Docker com `docker-compose logs`
4. **Database**: SQLite file `energy.db`

---

**Happy Coding! 🚀**
