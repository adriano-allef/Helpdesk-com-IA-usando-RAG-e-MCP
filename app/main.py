from fastapi import FastAPI
from sqlalchemy import text

# Importações das configurações
from database.database import engine
from models.models import Base

# Importação das nossas Rotas separadas
from routers import users, documents, chat

# 1. Configuração do Banco de Dados Vetorial
with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    conn.commit()

Base.metadata.create_all(bind=engine)

# 2. Inicialização da API
app = FastAPI(
    title="Helpdesk Institucional API",
    description="API com IA Generativa e Banco Vetorial (RAG) para Helpdesk"
)

# 3. Registrar as rotas (Os "departamentos" do sistema)
app.include_router(users.router)
app.include_router(documents.router)
app.include_router(chat.router)

@app.get("/", tags=["Health Check"])
def read_root():
    return {"mensagem": "Servidor rodando perfeitamente no Docker!"}