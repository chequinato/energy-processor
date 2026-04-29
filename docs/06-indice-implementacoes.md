# 📋 Índice de Implementações

## 🎯 Visão Geral

Este documento serve como guia rápido para localizar onde implementar cada funcionalidade no projeto Energy Data Processor.

---

## 🗂️ Estrutura de Arquivos

### Backend (`backend/`)
```
backend/
├── app/
│   ├── controllers/         # 📌 Endpoints HTTP
│   │   ├── upload_controller.py      # Upload e processamento
│   │   ├── auth_controller.py        # [NOVO] Autenticação
│   │   ├── dashboard_controller.py  # [NOVO] Endpoints dashboard
│   │   └── mobile_controller.py     # [NOVO] API mobile
│   ├── services/           # 📌 Lógica de negócio
│   │   ├── consumo_service.py       # Processamento principal
│   │   ├── alert_service.py        # [NOVO] Sistema de alertas
│   │   ├── dashboard_service.py     # [NOVO] Serviços dashboard
│   │   └── ml_service.py           # [NOVO] Machine Learning
│   ├── repositories/       # 📌 Acesso ao banco
│   │   ├── consumo_repository.py    # Operações consumo
│   │   ├── cliente_repository.py   # Operações cliente
│   │   └── alert_repository.py    # [NOVO] Alertas
│   ├── models/            # 📌 SQLAlchemy ORM
│   │   ├── consumo.py              # Modelo consumo
│   │   ├── cliente.py             # Modelo cliente
│   │   ├── upload.py              # Modelo upload
│   │   ├── user.py                # [NOVO] Modelo usuário
│   │   ├── organization.py       # [NOVO] Modelo organização
│   │   └── alert.py               # [NOVO] Modelo alerta
│   ├── schemas/           # 📌 Pydantic DTOs
│   │   ├── consumo.py              # Schema consumo
│   │   ├── cliente.py             # Schema cliente
│   │   ├── user.py                # [NOVO] Schema usuário
│   │   └── auth.py                # [NOVO] Schema auth
│   ├── core/              # 📌 Configurações
│   │   ├── database.py             # Configuração DB
│   │   ├── cache.py               # [NOVO] Sistema cache
│   │   ├── security.py            # [NOVO] Configurações JWT
│   │   └── postgres.py            # [NOVO] Configuração PG
│   ├── utils/             # 📌 Helpers
│   │   ├── validators.py           # Validações
│   │   ├── calculations.py        # Cálculos
│   │   ├── file_reader.py         # Leitura arquivos
│   │   ├── email_sender.py        # [NOVO] Envio emails
│   │   └── data_optimization.py  # [NOVO] Otimização dados
│   ├── auth/              # [NOVO] Autenticação
│   │   ├── models.py               # Modelos usuário
│   │   ├── schemas.py              # Schemas auth
│   │   ├── jwt_handler.py          # JWT tokens
│   │   └── dependencies.py        # Deps auth
│   ├── ml/                # [NOVO] Machine Learning
│   │   ├── models.py               # Modelos ML
│   │   ├── features.py             # Feature engineering
│   │   ├── training.py             # Pipeline treinamento
│   │   └── prediction.py           # Serviço previsão
│   ├── websocket/         # [NOVO] Real-time
│   │   ├── connection_manager.py    # Gerenciar conexões
│   │   ├── events.py              # Eventos domínio
│   │   └── handlers.py            # Handlers WebSocket
│   └── tasks/             # [NOVO] Tarefas assíncronas
│       ├── celery_app.py           # Configuração Celery
│       ├── data_processing.py      # Tarefas dados
│       └── notifications.py       # Tarefas notificação
├── main.py                 # 📌 Entry point FastAPI
├── Dockerfile              # 📌 Container backend
└── requirements.txt        # 📌 Dependências Python
```

### Frontend (`frontend/`)
```
frontend/
└── dashboard/
    ├── app.py                  # 📌 Aplicação principal
    ├── components/              # [NOVO] Componentes UI
    │   ├── charts.py             # Gráficos reutilizáveis
    │   ├── metrics.py            # KPIs components
    │   ├── filters.py            # Filtros avançados
    │   └── real_time.py         # Componentes real-time
    ├── pages/                  # [NOVO] Páginas separadas
    │   ├── dashboard.py          # Dashboard principal
    │   ├── analytics.py          # Análises avançadas
    │   ├── reports.py            # Relatórios
    │   └── settings.py          # Configurações
    ├── utils/                   # [NOVO] Utilitários frontend
    │   ├── api_client.py         # Cliente API
    │   ├── cache.py              # Cache local
    │   └── websocket_client.py   # Cliente WebSocket
    ├── Dockerfile              # 📌 Container frontend
    └── requirements.txt        # 📌 Dependências Python
```

---

## 🎯 Guia de Implementação por Feature

### 📊 Cache Inteligente
**Onde implementar**:
```python
# 1. Backend - Sistema de cache
backend/app/core/cache.py
├── redis_client.py      # Cliente Redis
├── cache_manager.py     # Gerenciador cache
└── decorators.py       # Cache decorators

# 2. Frontend - Cache otimizado
frontend/dashboard/utils/cache.py
├── api_cache.py        # Cache de chamadas API
└── state_cache.py      # Cache de estado

# 3. Modificar arquivos existentes
backend/app/services/consumo_service.py     # Adicionar @cache
frontend/dashboard/app.py                   # Adicionar @st.cache_data
```

**Arquivos a criar/modificar**:
- ✅ `backend/app/core/cache.py` (novo)
- ✅ `backend/requirements.txt` (adicionar redis)
- ✅ `frontend/dashboard/app.py` (modificar existing)

### 🔐 Autenticação JWT
**Onde implementar**:
```python
# 1. Models de usuário
backend/app/auth/models.py
├── User              # Modelo usuário
├── Role              # Modelo permissão
└── UserRole          # Relacionamento

# 2. JWT Handler
backend/app/auth/jwt_handler.py
├── create_token()     # Criar tokens
├── verify_token()     # Verificar tokens
└── refresh_token()    # Refresh tokens

# 3. Dependencies
backend/app/auth/dependencies.py
├── get_current_user()  # Usuário atual
└── get_current_admin() # Admin check

# 4. Controller
backend/app/controllers/auth_controller.py
├── /login            # Login endpoint
├── /register         # Registro endpoint
├── /refresh          # Refresh endpoint
└── /logout           # Logout endpoint
```

**Arquivos a criar/modificar**:
- ✅ `backend/app/auth/models.py` (novo)
- ✅ `backend/app/auth/schemas.py` (novo)
- ✅ `backend/app/auth/jwt_handler.py` (novo)
- ✅ `backend/app/auth/dependencies.py` (novo)
- ✅ `backend/app/controllers/auth_controller.py` (novo)
- ✅ `backend/main.py` (modificar existing)

### 🤖 Machine Learning
**Onde implementar**:
```python
# 1. Modelos ML
backend/app/ml/models.py
├── ConsumptionPredictor    # Previsão consumo
├── AnomalyDetector        # Detecção anomalia
└── EfficiencyModel       # Modelo eficiência

# 2. Feature Engineering
backend/app/ml/features.py
├── extract_temporal_features()  # Features tempo
├── extract_client_features()     # Features cliente
└── extract_price_features()      # Features preço

# 3. Training Pipeline
backend/app/ml/training.py
├── train_consumption_model()  # Treinar consumo
├── train_anomaly_model()      # Treinar anomalia
└── evaluate_models()          # Avaliar modelos

# 4. Prediction Service
backend/app/ml/prediction.py
├── predict_consumption()       # Prever consumo
├── detect_anomalies()         # Detectar anomalias
└── get_efficiency_score()    # Score eficiência

# 5. ML Controller
backend/app/controllers/ml_controller.py
├── /predictions/consumption   # Endpoint previsão
├── /anomalies/detect         # Endpoint anomalia
└── /models/retrain           # Endpoint retreino
```

**Arquivos a criar/modificar**:
- ✅ `backend/app/ml/models.py` (novo)
- ✅ `backend/app/ml/features.py` (novo)
- ✅ `backend/app/ml/training.py` (novo)
- ✅ `backend/app/ml/prediction.py` (novo)
- ✅ `backend/app/controllers/ml_controller.py` (novo)
- ✅ `backend/requirements.txt` (adicionar scikit-learn)

### 🔔 Sistema de Alertas
**Onde implementar**:
```python
# 1. Modelo de Alerta
backend/app/models/alert.py
├── Alert              # Modelo alerta
├── AlertType          # Tipos de alerta
└── AlertStatus        # Status alerta

# 2. Service de Alertas
backend/app/services/alert_service.py
├── check_consumption_anomalies()  # Verificar anomalias
├── check_growth_thresholds()       # Verificar crescimento
├── check_client_risk()            # Verificar risco
└── send_alerts()                 # Enviar alertas

# 3. Email Sender
backend/app/utils/email_sender.py
├── send_alert_email()     # Enviar email alerta
├── send_report_email()    # Enviar relatório
└── email_templates.py      # Templates email

# 4. Alert Controller
backend/app/controllers/alert_controller.py
├── /alerts/             # Listar alertas
├── /alerts/configure    # Configurar alertas
└── /alerts/acknowledge  # Reconhecer alertas
```

**Arquivos a criar/modificar**:
- ✅ `backend/app/models/alert.py` (novo)
- ✅ `backend/app/services/alert_service.py` (novo)
- ✅ `backend/app/utils/email_sender.py` (novo)
- ✅ `backend/app/controllers/alert_controller.py` (novo)

### 📱 Mobile API
**Onde implementar**:
```python
# 1. Mobile Controller
backend/app/controllers/mobile_controller.py
├── /mobile/resumo       # Resumo otimizado
├── /mobile/alertas       # Alertas mobile
├── /mobile/upload        # Upload simplificado
└── /mobile/offline      # Dados offline

# 2. Mobile Schemas
backend/app/schemas/mobile.py
├── MobileSummary        # Schema resumo
├── MobileAlert         # Schema alerta
└── MobileUpload        # Schema upload

# 3. Mobile Service
backend/app/services/mobile_service.py
├── get_optimized_summary()  # Dados otimizados
├── get_push_notifications() # Notificações push
└── sync_offline_data()     # Sync dados
```

**Arquivos a criar/modificar**:
- ✅ `backend/app/controllers/mobile_controller.py` (novo)
- ✅ `backend/app/schemas/mobile.py` (novo)
- ✅ `backend/app/services/mobile_service.py` (novo)

### ⚡ Dashboard em Tempo Real
**Onde implementar**:
```python
# 1. WebSocket Manager
backend/app/websocket/connection_manager.py
├── ConnectionManager    # Gerenciar conexões
├── broadcast()         # Broadcast mensagem
└── send_personal()     # Mensagem individual

# 2. WebSocket Events
backend/app/websocket/events.py
├── data_updated()      # Evento dados atualizados
├── alert_triggered()    # Evento alerta
└── new_upload()        # Evento novo upload

# 3. WebSocket Handlers
backend/app/websocket/handlers.py
├── handle_websocket()   # Handler principal
├── handle_subscribe()   # Inscrição eventos
└── handle_unsubscribe() # Cancelar inscrição

# 4. Frontend WebSocket Client
frontend/dashboard/utils/websocket_client.py
├── WebSocketClient     # Cliente WebSocket
├── connect()          # Conectar ao server
└── handle_message()   # Processar mensagens

# 5. Real-time Components
frontend/dashboard/components/real_time.py
├── RealTimeKPIs       # KPIs em tempo real
├── LiveAlerts          # Alertas ao vivo
└── AutoRefreshCharts    # Gráficos auto-refresh
```

**Arquivos a criar/modificar**:
- ✅ `backend/app/websocket/connection_manager.py` (novo)
- ✅ `backend/app/websocket/events.py` (novo)
- ✅ `backend/app/websocket/handlers.py` (novo)
- ✅ `frontend/dashboard/utils/websocket_client.py` (novo)
- ✅ `frontend/dashboard/components/real_time.py` (novo)

---

## 🔧 Implementação Passo a Passo

### Template para Nova Feature
```bash
# 1. Criar branch
git checkout -b feature/nova-feature

# 2. Backend
mkdir -p backend/app/{models,services,controllers,utils}
touch backend/app/models/novo_modelo.py
touch backend/app/services/novo_service.py
touch backend/app/controllers/novo_controller.py
touch backend/app/utils/novo_util.py

# 3. Frontend
mkdir -p frontend/dashboard/{components,utils,pages}
touch frontend/dashboard/components/novo_componente.py
touch frontend/dashboard/utils/novo_util.py
touch frontend/dashboard/pages/nova_pagina.py

# 4. Testes
mkdir -p tests/{unit,integration}
touch tests/unit/test_novo_service.py
touch tests/integration/test_novo_controller.py

# 5. Documentação
touch docs/nova-feature.md
```

### Checklist de Implementação
- [ ] **Model**: Criar modelo SQLAlchemy
- [ ] **Repository**: Implementar acesso a dados
- [ ] **Service**: Implementar lógica de negócio
- [ ] **Controller**: Criar endpoints HTTP
- [ ] **Schema**: Definir schemas Pydantic
- [ ] **Frontend**: Implementar UI components
- [ ] **Testes**: Criar testes unitários e integração
- [ ] **Docs**: Documentar nova feature
- [ ] **CI**: Atualizar workflows se necessário

---

## 🗂️ Mapa Rápido de Arquivos

### Para Adicionar Novo Endpoint
1. **Controller**: `backend/app/controllers/novo_controller.py`
2. **Service**: `backend/app/services/novo_service.py`
3. **Repository**: `backend/app/repositories/novo_repository.py`
4. **Model**: `backend/app/models/novo_modelo.py`
5. **Schema**: `backend/app/schemas/novo_schema.py`
6. **Main**: Adicionar router em `backend/main.py`

### Para Adicionar Novo Gráfico
1. **Componente**: `frontend/dashboard/components/novo_grafico.py`
2. **Utils**: `frontend/dashboard/utils/chart_utils.py`
3. **Página**: `frontend/dashboard/pages/pagina_grafico.py`
4. **App**: Importar em `frontend/dashboard/app.py`

### Para Adicionar Novo Cálculo
1. **Utils**: `backend/app/utils/novo_calculo.py`
2. **Service**: Integrar em `backend/app/services/consumo_service.py`
3. **Frontend**: Adicionar em `frontend/dashboard/app.py`

---

## 📋 Referência Rápida

### Endpoints Padrão
```python
# CRUD básico
GET    /api/recurso          # Listar todos
GET    /api/recurso/{id}     # Listar um
POST   /api/recurso          # Criar novo
PUT    /api/recurso/{id}     # Atualizar
DELETE /api/recurso/{id}     # Deletar

# Custom endpoints
POST   /api/recurso/process   # Processar dados
GET    /api/recurso/stats     # Estatísticas
POST   /api/recurso/upload    # Upload arquivo
```

### Padrões de Código
```python
# Controller pattern
@router.post("/api/novo")
async def create_novo(
    data: NovoSchema,
    db: Session = Depends(get_db)
):
    return novo_service.create(db, data)

# Service pattern
def create_novo(db: Session, data: NovoSchema):
    novo = NovoModel(**data.dict())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo

# Repository pattern
def create(db: Session, novo: NovoModel):
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo
```

### Frontend Pattern
```python
# Cache pattern
@st.cache_data(ttl=300)
def get_api_data():
    response = requests.get(f"{API_URL}/endpoint")
    return response.json()

# Component pattern
def render_novo_componente(data):
    st.subheader("Novo Componente")
    st.metric("Valor", data["valor"])
    # mais componentes...
```

---

## 🔍 Debug e Troubleshooting

### Logs por Componente
```python
# Backend logs
logger.info(f"Controller: {__name__} - Iniciando processamento")
logger.debug(f"Service: {service_name} - Dados: {data}")
logger.error(f"Repository: {repo_name} - Erro: {str(e)}")

# Frontend logs
st.write(f"Debug: Componente {component_name} carregado")
st.write(f"Debug: Dados recebidos: {len(data)} registros")
```

### Testes Locais
```bash
# Testar backend
cd backend
python -c "from app.controllers.novo_controller import router; print('OK')"

# Testar frontend
cd frontend/dashboard
streamlit run app.py --server.port 8502
```

---

## 📝 Boas Práticas

### Organização de Código
1. **Um arquivo por responsabilidade**
2. **Nomes descritivos** em português
3. **Docstrings** em todas as funções
4. **Type hints** obrigatórios
5. **Tratamento de erros** consistente

### Git Flow
1. **Branch**: `feature/nome-feature`
2. **Commit**: `feat: descrição da feature`
3. **PR**: Sempre com template
4. **Review**: Code review obrigatório
5. **Merge**: Squash and merge

### Documentação
1. **API Docs**: Atualizar OpenAPI
2. **User Docs**: Atualizar docs/
3. **Changelog**: Manter CHANGELOG.md
4. **Comments**: Código bem comentado

---

## 🎯 Próximos Passos

### Para Começar Imediatamente
1. **Cache Inteligente** (Fase 1)
   - Criar `backend/app/core/cache.py`
   - Modificar `frontend/dashboard/app.py`
   - Testar performance

2. **Autenticação JWT** (Fase 2)
   - Criar estrutura `backend/app/auth/`
   - Implementar login/logout
   - Proteger endpoints

3. **Sistema de Alertas** (Fase 2)
   - Criar modelo de alertas
   - Implementar verificações
   - Adicionar envio de email

### Para Planejar Futuramente
1. **Machine Learning** (Fase 3)
2. **Dashboard Real-time** (Fase 3)
3. **Mobile API** (Fase 4)

---

## 📞 Suporte e Ajuda

### Onde Pedir Ajuda
- **Dúvidas técnicas**: Canal #dev-help no Slack
- **Arquitetura**: Tech Lead em reuniões semanais
- **Code Review**: Pull requests no GitHub
- **Emergências**: Contato direto do Tech Lead

### Recursos Internos
- **Wiki**: Documentação completa em `/docs`
- **API Docs**: `http://localhost:8000/docs`
- **Dashboard**: `http://localhost:8501`
- **CI/CD**: GitHub Actions logs

---

*Última atualização: 29/04/2026*
**Próxima revisão: 29/05/2026*
