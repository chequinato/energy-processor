⚡ Energy Data Processor

Sistema para processamento e análise de consumo de energia com API + Dashboard.

🚀 Funcionalidades
Upload de arquivos CSV/Excel
Processamento e validação de dados
Cálculo de consumo e custo
API REST com FastAPI
Dashboard interativo com Streamlit
Geração de relatórios (PDF)
🏗️ Arquitetura
Backend: FastAPI + SQLAlchemy
Frontend: Streamlit + Plotly
Banco: SQLite
Infra: Docker
▶️ Como rodar
🔹 Com Docker (recomendado)
docker-compose up --build

Acessos:

API: http://localhost:8000
Docs: http://localhost:8000/docs
Dashboard: http://localhost:8501
🔹 Sem Docker
# backend
uvicorn backend.main:app --reload

# frontend
streamlit run frontend/dashboard/app.py
📊 Exemplo de uso
curl -F file=@arquivo.xlsx http://localhost:8000/api/upload
📁 Estrutura
backend/     # API FastAPI
frontend/    # Dashboard Streamlit
data/        # uploads
docs/        # documentação completa
📚 Documentação completa

👉 Veja em: docs/projeto-completo.md

🔮 Melhorias futuras
Autenticação JWT
PostgreSQL
CI/CD
Testes automatizados
