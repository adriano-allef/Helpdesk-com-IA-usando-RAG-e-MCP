import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 0. Ler as variáveis de ambiente que o Doker Compose passou para o container
# O os.getenv pega o valor. 
# Fazer checagem de segurança, se não encontrar as credenciais quebra o código!
DB_USER = os.getenv("DB_USER")
if not DB_USER:
    raise ValueError("ERRO CRÍTICO: A variável DB_USER não foi configurada no ambiente!")

DB_PASSWORD = os.getenv("DB_PASSWORD")
if not DB_PASSWORD:
    raise ValueError("ERRO CRÍTICO: A variável DB_PASSWORD não foi configurada no ambiente!")

DB_HOST = os.getenv("DB_HOST")
if not DB_HOST:
    raise ValueError("ERRO CRÍTICO: A variável DB_HOST não foi configurada no ambiente!")

DB_PORT = os.getenv("DB_PORT")
if not DB_PORT:
    raise ValueError("ERRO CRÍTICO: A variável DB_PORT não foi configurada no ambiente!")

DB_NAME = os.getenv("DB_NAME")
if not DB_NAME:
    raise ValueError("ERRO CRÍTICO: A variável DB_NAME não foi configurada no ambiente!")

# 1. A String de Conexão (A URL exata para achar o banco)
# O formato obrigatório do PostgreSQL é: postgresql://usuario:senha@host:porta/banco
SQLALCHEMY_DATABASE_URL = F"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 2. O Motor (Engine)
# O engine é o "motor" que gerencia as conversas entre o Python e o PostgreSQL.
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 3. A Fábrica de Sessoes (SessionLocal)
# Uma "Sessão" é uma janela de trabalho. Sempre que formos salvar um usuário ou ler um ticket,
# vou pedir uma sessão nova para esta fábrica. Quando terminar, a sessão será fechada.
# aautocommit=False impede que o banco salve coisas pela metade caso dê algum erro no meio do caminho.

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. A Base(O Molde Principal)
# Esta é a exata variável importei lá no 'models.py'!
# É ela que avisa o motor do SQLAlchemy sobre quais classes existem para virarem tabelas.
Base = declarative_base()

#Esta função abre uma sessão com o abnco e garante que ela seja fechada após o uso.

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()