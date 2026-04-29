# 🐳 Docker e Containerização

## 🎯 Visão Geral

O Energy Data Processor utiliza Docker para containerização completa da aplicação, garantindo consistência entre ambientes de desenvolvimento e produção.

---

## 📁 Estrutura Docker

### Docker Compose Principal
```yaml
# docker-compose.yml
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

#### Backend Dockerfile
```dockerfile
FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Frontend Dockerfile
```dockerfile
FROM python:3.11-slim-bookworm

WORKDIR /app

# Dependências do sistema + Chrome para PDF
RUN apt-get update && apt-get install -y \
    wget gnupg ca-certificates libnss3 \
    libatk-bridge2.0-0 libcups2 libxcomposite1 \
    libxdamage1 libxfixes3 libxrandr2 libgbm1 \
    libxkbcommon0 libpango-1.0-0 libcairo2 \
    libasound2 fonts-liberation \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | \
    gpg --dearmor -o /usr/share/keyrings/google.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/google.gpg] \
    http://dl.google.com/linux/chrome/deb/ stable main" > \
    /etc/apt/sources.list.d/google.list \
    && apt-get update && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

---

## 🚀 Comandos Principais

### Desenvolvimento
```bash
# Iniciar todos os serviços
docker compose up

# Iniciar em background
docker compose up -d

# Reconstruir e iniciar
docker compose up --build

# Parar serviços
docker compose down

# Parar e remover volumes
docker compose down -v
```

### Build e Debug
```bash
# Apenas build sem iniciar
docker compose build

# Build de serviço específico
docker compose build backend
docker compose build frontend

# Ver logs em tempo real
docker compose logs -f
docker compose logs -f backend
docker compose logs -f frontend

# Executar comando no container
docker compose exec backend bash
docker compose exec frontend bash
```

### Manutenção
```bash
# Limpar imagens não usadas
docker image prune -f

# Limpar containers e volumes
docker system prune -af

# Ver status dos containers
docker compose ps

# Ver consumo de recursos
docker stats
```

---

## 📁 Volumes e Persistência

### Volumes Configurados
```yaml
volumes:
  # Banco de dados persistente
  - ./energy.db:/app/energy.db
  
  # Uploads de arquivos
  - ./data:/app/data
```

### Estrutura de Volumes
```
project/
├── energy.db          # Banco SQLite persistente
└── data/
    └── uploads/       # Arquivos CSV/Excel
        ├── planilha1.xlsx
        ├── dados.csv
        └── ...
```

### Backup de Volumes
```bash
# Backup do banco
docker compose exec backend cp /app/energy.db ./backup/energy_$(date +%Y%m%d).db

# Backup dos uploads
docker compose exec frontend cp -r /app/data/uploads ./backup/uploads_$(date +%Y%m%d)

# Restaurar backup
docker compose exec -d backend cp ./backup/energy_20240429.db /app/energy.db
```

---

## 🔧 Configuração de Rede

### Port Mapping
- **Backend**: `8000:8000` (API FastAPI)
- **Frontend**: `8501:8501` (Dashboard Streamlit)
- **Redis**: `6379:6379` (Cache)

### Comunicação Interna
```yaml
# Frontend acessa backend via nome do serviço
API_URL = "http://backend:8000/api"

# Backend acessa frontend (se necessário)
FRONTEND_URL = "http://frontend:8501"
```

### DNS Interno
- `backend`: Resolvido para IP do container backend
- `frontend`: Resolvido para IP do container frontend
- `redis`: Resolvido para IP do container Redis

---

## 🏗️ Build Optimization

### Multi-stage Builds
```dockerfile
# Backend otimizado
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Layer Caching
```dockerfile
# Ordem otimizada para cache
COPY requirements.txt .      # Muda pouco
RUN pip install -r requirements.txt  # Cache se requirements.txt mudar
COPY . .                    # Muda sempre
```

---

## 🔒 Segurança

### Best Practices
```dockerfile
# Usar usuário não-root
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# Remover dependências de build
RUN apt-get remove -y wget gnupg && apt-get autoremove -y

# Expor apenas portas necessárias
EXPOSE 8000

# Read-only filesystem (quando possível)
```

### Secrets Management
```bash
# Arquivo .env para secrets
echo "DATABASE_URL=sqlite:///./energy.db" > .env
echo "SECRET_KEY=your-secret-key" >> .env

# No docker-compose.yml
environment:
  - DATABASE_URL=${DATABASE_URL}
  - SECRET_KEY=${SECRET_KEY}
```

---

## 📊 Monitoramento e Logs

### Logs Estruturados
```yaml
# docker-compose.yml com logging
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### Health Checks
```dockerfile
# No Dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/docs || exit 1
```

### Monitoramento
```bash
# Ver consumo de recursos
docker stats --no-stream

# Ver eventos do Docker
docker events --filter event=oom

# Inspect container
docker inspect energy-processor-backend-1
```

---

## 🚀 Deploy em Produção

### Docker Compose Produção
```yaml
version: "3.9"

services:
  backend:
    image: energy-processor-backend:latest
    restart: unless-stopped
    environment:
      - ENV=production
      - DATABASE_URL=${DB_URL}
    volumes:
      - postgres_data:/app/data
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1.0'
          memory: 512M

  frontend:
    image: energy-processor-frontend:latest
    restart: unless-stopped
    environment:
      - ENV=production
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '0.5'
          memory: 256M

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl
    depends_on:
      - backend
      - frontend
```

### Orquestração com Kubernetes
```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: energy-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: energy-backend
  template:
    metadata:
      labels:
        app: energy-backend
    spec:
      containers:
      - name: backend
        image: energy-processor-backend:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

---

## 🔧 Troubleshooting Comum

### Problemas Frequentes

#### 1. Port Already in Use
```bash
# Ver processos usando portas
netstat -tulpn | grep :8000
netstat -tulpn | grep :8501

# Matar processos
sudo kill -9 <PID>

# Ou mudar portas no docker-compose.yml
ports:
  - "8001:8000"  # Usar porta diferente
```

#### 2. Permission Denied
```bash
# Corrigir permissões de volumes
sudo chown -R $USER:$USER ./data
sudo chmod -R 755 ./data

# Ou usar Docker com sudo
sudo docker compose up
```

#### 3. Build Fails
```bash
# Limpar cache completo
docker system prune -af
docker compose down --volumes
docker compose up --build

# Ver logs de build
docker compose build --no-cache --progress=plain
```

#### 4. Container Não Inicia
```bash
# Ver logs detalhados
docker compose logs backend
docker compose logs frontend

# Entrar no container para debug
docker compose exec backend bash
docker compose exec frontend bash

# Ver status dos serviços
docker compose ps
```

---

## 📝 Scripts Úteis

### Script de Deploy
```bash
#!/bin/bash
# deploy.sh

echo "🚀 Iniciando deploy..."

# Parar serviços antigos
docker compose down

# Pull de novas imagens
docker compose pull

# Build local (se necessário)
docker compose build

# Iniciar novos serviços
docker compose up -d

# Verificar saúde
sleep 10
docker compose ps

echo "✅ Deploy concluído!"
```

### Script de Backup
```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups"

mkdir -p $BACKUP_DIR

# Backup banco
docker compose exec -T backend cp /app/energy.db $BACKUP_DIR/energy_$DATE.db

# Backup uploads
docker compose exec -T frontend tar -czf - /app/data/uploads > $BACKUP_DIR/uploads_$DATE.tar.gz

echo "✅ Backup concluído: $BACKUP_DIR"
```

### Script de Limpeza
```bash
#!/bin/bash
# cleanup.sh

echo "🧹 Limpando recursos Docker..."

# Remover containers parados
docker container prune -f

# Remover imagens não usadas
docker image prune -f

# Remover volumes não usados
docker volume prune -f

echo "✅ Limpeza concluída!"
```

---

## 📋 Comandos de Referência Rápida

### Essenciais
```bash
docker compose up -d                    # Iniciar em background
docker compose down                     # Parar tudo
docker compose logs -f                   # Ver logs
docker compose exec backend bash          # Acessar backend
docker compose exec frontend bash         # Acessar frontend
```

### Manutenção
```bash
docker compose build                    # Reconstruir imagens
docker compose pull                    # Atualizar imagens
docker system prune -f                # Limpar sistema
docker compose restart                 # Reiniciar serviços
```

### Debug
```bash
docker compose ps                      # Ver status
docker compose logs backend            # Logs backend
docker compose logs frontend           # Logs frontend
docker stats                         # Recursos em tempo real
```

---

## 🎯 Boas Práticas

### Development
1. **Sempre usar volumes** para persistência
2. **Variáveis de ambiente** no .env
3. **Rebuild apenas quando necessário**
4. **Logs em arquivos** para debug

### Production
1. **Imagens otimizadas** (multi-stage)
2. **Health checks** configurados
3. **Resource limits** definidos
4. **Backup automático** de volumes
5. **Monitoramento** ativo

### Security
1. **Usuário não-root** nos containers
2. **Secrets externos** (não no código)
3. **Portas mínimas** expostas
4. **Imagens oficiais** como base

---

*Última atualização: 29/04/2026*
