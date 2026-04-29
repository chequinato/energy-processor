# 🚀 CI/CD com GitHub Actions

## 🎯 Visão Geral

O Energy Data Processor utiliza GitHub Actions para automação de builds, testes e deploy, garantindo qualidade e consistência em todas as mudanças.

---

## 📁 Estrutura de Workflows

### Diretório de Workflows
```
.github/
└── workflows/
    ├── ci.yml              # Pipeline principal de CI
    ├── deploy-staging.yml   # Deploy para staging
    ├── deploy-prod.yml     # Deploy para produção
    └── security.yml        # Scans de segurança
```

---

## 🔄 Pipeline Principal (CI)

### Workflow: `.github/workflows/ci.yml`
```yaml
name: CI - Energy Data Processor

on:
  push:
    branches: ["main", "develop"]
  pull_request:
    branches: ["main"]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11"]

    steps:
      - name: Checkout código
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-

      - name: Instalar dependências backend
        run: |
          cd backend
          pip install -r requirements.txt

      - name: Teste básico de import
        run: |
          cd backend
          python -c "import main; print('backend OK 🔥')"

      - name: Lint com flake8
        run: |
          cd backend
          pip install flake8
          flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

  docker:
    runs-on: ubuntu-latest
    needs: test

    steps:
      - name: Checkout código
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to Docker Hub
        if: github.ref == 'refs/heads/main'
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build Docker Compose
        run: |
          docker compose build

      - name: Test containers
        run: |
          docker compose up -d
          sleep 30
          docker compose ps
          
          # Health check backend
          curl -f http://localhost:8000/docs || exit 1
          
          # Health check frontend
          curl -f http://localhost:8501 || exit 1

      - name: Push to Docker Hub
        if: github.ref == 'refs/heads/main'
        run: |
          docker tag energy-processor-backend:latest ${{ secrets.DOCKER_USERNAME }}/energy-processor-backend:latest
          docker tag energy-processor-frontend:latest ${{ secrets.DOCKER_USERNAME }}/energy-processor-frontend:latest
          
          docker push ${{ secrets.DOCKER_USERNAME }}/energy-processor-backend:latest
          docker push ${{ secrets.DOCKER_USERNAME }}/energy-processor-frontend:latest

      - name: Cleanup
        run: |
          docker compose down -v
          docker system prune -f
```

---

## 🚀 Deploy Staging

### Workflow: `.github/workflows/deploy-staging.yml`
```yaml
name: Deploy Staging

on:
  push:
    branches: ["develop"]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: staging

    steps:
      - name: Checkout código
        uses: actions/checkout@v4

      - name: Deploy to staging
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.STAGING_HOST }}
          username: ${{ secrets.STAGING_USER }}
          key: ${{ secrets.STAGING_SSH_KEY }}
          script: |
            cd /opt/energy-processor
            git pull origin develop
            docker compose down
            docker compose build
            docker compose up -d
            
            # Wait for services
            sleep 30
            
            # Health checks
            curl -f http://localhost:8000/docs || exit 1
            curl -f http://localhost:8501 || exit 1
            
            echo "✅ Deploy staging concluído!"

      - name: Notify Slack
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          channel: '#deployments'
          text: |
            🚀 *Deploy Staging*
            Branch: ${{ github.ref_name }}
            Commit: ${{ github.sha }}
            Status: ${{ job.status }}
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

---

## 🏭 Deploy Produção

### Workflow: `.github/workflows/deploy-prod.yml`
```yaml
name: Deploy Production

on:
  push:
    tags: ["v*"]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production

    steps:
      - name: Checkout código
        uses: actions/checkout@v4

      - name: Create Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ github.ref }}
          draft: false
          prerelease: false

      - name: Deploy to production
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.PROD_HOST }}
          username: ${{ secrets.PROD_USER }}
          key: ${{ secrets.PROD_SSH_KEY }}
          script: |
            cd /opt/energy-processor
            
            # Backup atual
            ./scripts/backup.sh
            
            # Deploy novo
            git pull origin main
            docker compose down
            docker compose build
            docker compose up -d
            
            # Wait for services
            sleep 60
            
            # Health checks
            curl -f http://localhost:8000/docs || exit 1
            curl -f http://localhost:8501 || exit 1
            
            # Verify data integrity
            python scripts/verify_data.py
            
            echo "✅ Deploy produção concluído!"

      - name: Smoke Tests
        run: |
          # Testes automatizados em produção
          python scripts/smoke_tests.py --env=production

      - name: Notify Teams
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          channel: '#deployments'
          text: |
            🏭 *Deploy Produção*
            Versão: ${{ github.ref_name }}
            Commit: ${{ github.sha }}
            Status: ${{ job.status }}
            Link: https://energy.seudominio.com
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

---

## 🔒 Segurança

### Workflow: `.github/workflows/security.yml`
```yaml
name: Security Scan

on:
  schedule:
    - cron: '0 2 * * 1'  # Segunda 2h da manhã
  push:
    branches: [main]

jobs:
  security:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout código
        uses: actions/checkout@v4

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload Trivy scan results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

      - name: Python security scan
        uses: PyCQA/bandit-action@v1
        with:
          path: backend/

      - name: Dependency check
        run: |
          cd backend
          pip install safety
          safety check --json --output safety-report.json || true

      - name: Security Score
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const report = JSON.parse(fs.readFileSync('safety-report.json', 'utf8'));
            console.log(`🔒 Security Score: ${report.vulnerabilities.length} issues found`);
```

---

## 🔧 Configuração de Secrets

### Secrets Necessários
```bash
# Docker Hub
DOCKER_USERNAME=seu_usuario_docker
DOCKER_PASSWORD=sua_senha_docker

# Deploy Staging
STAGING_HOST=seu_servidor_staging.com
STAGING_USER=deploy
STAGING_SSH_KEY=-----BEGIN RSA...

# Deploy Produção
PROD_HOST=seu_servidor_prod.com
PROD_USER=deploy
PROD_SSH_KEY=-----BEGIN RSA...

# Notificações
SLACK_WEBHOOK=https://hooks.slack.com/...
TEAMS_WEBHOOK=https://outlook.office.com/...

# GitHub Token (automático)
GITHUB_TOKEN=ghp_...
```

### Configurar Secrets no GitHub
1. Ir para **Settings** → **Secrets and variables** → **Actions**
2. Clicar **New repository secret**
3. Adicionar cada secret acima
4. Marcar como **Environment secret** quando aplicável

---

## 📋 Scripts de Deploy

### Script de Backup (`scripts/backup.sh`)
```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups"

mkdir -p $BACKUP_DIR

# Backup banco
docker compose exec -T backend cp /app/energy.db $BACKUP_DIR/energy_$DATE.db

# Backup uploads
docker compose exec -T frontend tar -czf - /app/data/uploads > $BACKUP_DIR/uploads_$DATE.tar.gz

# Limpar backups antigos (manter 7 dias)
find $BACKUP_DIR -name "*.db" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "✅ Backup concluído: $DATE"
```

### Script de Verificação (`scripts/verify_data.py`)
```python
#!/usr/bin/env python3
# verify_data.py

import requests
import sys

def verify_backend():
    try:
        response = requests.get("http://localhost:8000/api/clientes", timeout=10)
        return response.status_code == 200
    except:
        return False

def verify_frontend():
    try:
        response = requests.get("http://localhost:8501", timeout=10)
        return response.status_code == 200
    except:
        return False

def verify_data_integrity():
    try:
        response = requests.get("http://localhost:8000/api/consumos", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return len(data) > 0
        return False
    except:
        return False

if __name__ == "__main__":
    print("🔍 Verificando integridade do deploy...")
    
    if not verify_backend():
        print("❌ Backend não responde")
        sys.exit(1)
    
    if not verify_frontend():
        print("❌ Frontend não responde")
        sys.exit(1)
    
    if not verify_data_integrity():
        print("❌ Dados inconsistentes")
        sys.exit(1)
    
    print("✅ Verificação concluída com sucesso!")
```

### Script de Smoke Tests (`scripts/smoke_tests.py`)
```python
#!/usr/bin/env python3
# smoke_tests.py

import argparse
import requests
import json

def test_upload():
    """Teste de upload de arquivo"""
    # Implementar teste de upload
    pass

def test_endpoints():
    """Teste de endpoints principais"""
    base_url = "http://localhost:8000/api"
    
    endpoints = [
        "/consumos",
        "/clientes", 
        "/relatorios",
        "/uploads"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code != 200:
                print(f"❌ Endpoint {endpoint} falhou: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Erro no endpoint {endpoint}: {e}")
            return False
    
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", required=True, choices=["staging", "production"])
    args = parser.parse_args()
    
    base_url = "http://localhost:8000" if args.env == "staging" else "https://energy.seudominio.com"
    
    print(f"🧪 Smoke Tests - Environment: {args.env}")
    
    if not test_endpoints():
        print("❌ Smoke tests falharam")
        exit(1)
    
    print("✅ Smoke tests passaram")

if __name__ == "__main__":
    main()
```

---

## 📊 Monitoramento e Logs

### Logs do GitHub Actions
```bash
# Ver logs de um workflow específico
gh run view --log <run-id>

# Ver todos os runs recentes
gh run list

# Baixar artifacts
gh run download <run-id>
```

### Monitoramento de Deploy
```yaml
# Adicionar ao workflow
- name: Setup monitoring
  run: |
    # Instalar agent de monitoramento
    curl -L https://github.com/monitoring/agent.sh | bash
    
    # Configurar health checks
    echo "*/5 * * * * curl -f http://localhost:8000/health" | crontab -
```

### Alertas Automáticos
```yaml
- name: Health Check
  run: |
    # Verificar se serviços estão online
    for i in {1..6}; do
      if curl -f http://localhost:8000/docs; then
        echo "✅ Backend healthy"
        break
      else
        echo "⏳ Waiting for backend... ($i/6)"
        sleep 10
      fi
    done
    
    if [ $i -eq 6 ]; then
      echo "❌ Backend failed to start"
      exit 1
    fi
```

---

## 🔄 Branch Strategy

### Git Flow
```
main (produção)
├── develop (staging)
│   ├── feature/nova-funcionalidade
│   ├── feature/melhoria-dashboard
│   └── hotfix/correcao-urgente
└── tags (v1.0.0, v1.1.0, ...)
```

### Regras de Branch
- **main**: Apenas deploy automático para produção
- **develop**: Deploy automático para staging
- **feature/***: Pull requests para develop
- **hotfix/***: Pull requests direto para main

### Versionamento Semântico
```
v1.0.0  # Major (quebra de compatibilidade)
v1.1.0  # Minor (novas funcionalidades)
v1.1.1  # Patch (correções de bugs)
```

---

## 🎯 Boas Práticas

### Performance
1. **Cache de dependências** no GitHub Actions
2. **Matrix builds** para múltiplas versões
3. **Paralelização** de jobs
4. **Artifacts** para compartilhar dados

### Segurança
1. **Secrets** para credenciais
2. **Environment protection** para produção
3. **Security scans** automatizados
4. **Least privilege** para acessos

### Confiabilidade
1. **Health checks** pós-deploy
2. **Rollback automático** em falhas
3. **Smoke tests** automatizados
4. **Notificações** de status

---

## 📝 Exemplos de Workflows

### Workflow Customizado
```yaml
name: Custom Tests

on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment'
        required: true
        default: 'staging'
        type: choice
        options:
        - staging
        - production

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Run custom tests
        run: |
          echo "Running tests on ${{ github.event.inputs.environment }}"
          python scripts/custom_tests.py --env=${{ github.event.inputs.environment }}
```

### Multi-Environment Deploy
```yaml
- name: Deploy
  run: |
    if [[ "${{ github.ref }}" == "refs/heads/main" ]]; then
      echo "Deploying to production"
      # comandos prod
    elif [[ "${{ github.ref }}" == "refs/heads/develop" ]]; then
      echo "Deploying to staging"
      # comandos staging
    fi
```

---

## 🚀 Otimizações Avançadas

### Cache Inteligente
```yaml
- name: Cache Docker layers
  uses: actions/cache@v3
  with:
    path: /tmp/.buildx-cache
    key: ${{ runner.os }}-buildx-${{ github.sha }}
    restore-keys: |
      ${{ runner.os }}-buildx-
```

### Matrix Strategies
```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest]
    python-version: ['3.11', '3.10']
    include:
      - os: ubuntu-latest
        python-version: '3.11'
        experimental: true
```

### Conditional Deployments
```yaml
- name: Deploy
  if: |
    github.ref == 'refs/heads/main' && 
    github.event_name == 'push' &&
    !contains(github.event.head_commit.message, '[skip-deploy]')
  run: |
    echo "Deploying..."
```

---

## 📋 Comandos Úteis

### CLI do GitHub
```bash
# Ver workflows
gh workflow list

# Disparar workflow manual
gh workflow run "Custom Tests" --field environment=staging

# Ver runs
gh run list --workflow="CI - Energy Data Processor"

# Cancelar run
gh run cancel <run-id>

# Ver logs
gh run view <run-id> --log
```

### Debug Local
```bash
# Testar workflow localmente
act -j test

# Ver secrets (debug apenas)
gh secret list

# Ver environment rules
gh api repos/:owner/:repo/environments
```

---

## 🔍 Troubleshooting

### Problemas Comuns

#### 1. Secrets não encontrados
```bash
# Verificar secrets disponíveis
gh secret list

# Adicionar secret faltante
gh secret set NOME_DO_SECRET --body "valor_do_secret"
```

#### 2. Timeout no deploy
```yaml
# Aumentar timeout
- name: Deploy
  timeout-minutes: 30
  run: |
    # comandos de deploy
```

#### 3. Permissões SSH
```bash
# Gerar chave SSH correta
ssh-keygen -t rsa -b 4096 -C "github-actions"

# Adicionar chave ao servidor
ssh-copy-id -i ~/.ssh/id_rsa user@server
```

---

*Última atualização: 29/04/2026*
