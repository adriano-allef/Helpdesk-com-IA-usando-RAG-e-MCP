import os
import google.generativeai as genai
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError # <-- O capturador de erros do banco 
from sqlalchemy import text

#Importações das pastas
from database.database import engine, SessionLocal
from models.models import Base
import models.models as models #para usar o models.User
import schemas.schemas as schemas # Para usar schemas.UserCreate
from datetime import datetime


# 2. O camando do SQLAlchemy:
#Liga a extensão matemática no PostgreSQL
with engine.connect() as conn:
    conn. execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    conn.commit()
# "Cria a tabela no banco"
Base.metadata.create_all(bind=engine)

#Inicializa o aplicativo FastAPI
app = FastAPI(title="Helpdesk Institucional API")

# --- NOVA FUNÇÃO: Gerenciador de Banco de Dados ---
#Esta função abre uma sessão com o abnco e garante que ela seja fechada após o uso.

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---- PRIMEIRA ROTA (ENDPOINT) REAL ---
# Usei @app.post porque estou ENVIANDO DADOS PARA CRIAR ALGO NOVO.
# response_model=schemas.UserResponse avisa o FastAPI para usar o Pydantic para formatar a saída.
@app.post("/users", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    # 1. Tradução: Peguei os dados validadeos pelo Pydantic (user)
    # e transformei no formato que o SQLALchemy entende (models.User)
    db_user = models.User(nome=user.nome, email=user.email, papel=user.papel)

    db.add(db_user)

    try:
        db.commit()# tenta salvar
        db.refresh(db_user)
        return db_user

    except IntegrityError:
        #Se der erro de e-mail duplicado, o código cai direto aqui!

        #1. Rollback: Desfaz a transação travada no banco (EXTREMAMENTE IMPORTANTE)
        db.rollback()

        #2. Levanta um erro amigável (Status 400) para quem chamou a API
        raise HTTPException(
            status_code=400,
            detail="Este e-mail já está cadastrado no sistema."
        )
    
@app.post("/documents", response_model=schemas.DocumentResponse)
def create_document(document: schemas.DocumentCreate, db: Session = Depends(get_db)):
    
    # 1. Segurança Fail-Fast: Vai buscar a chave ao .env
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise HTTPException(status_code=500, detail="Chave da IA não configurada no servidor.")
    
    # 2. Configura a IA
    genai.configure(api_key=gemini_key)
    
    try:
        # 3. Pede à IA para transformar o texto num vetor (Embedding)
        resposta_ia = genai.embed_content(
            model="models/gemini-embedding-001",
            content=document.conteudo,
            task_type="retrieval_document", # Ajuda a IA a otimizar o vetor para ser "buscado" depois
            output_dimensionality=768 #<-- força o tamanho do vetor, em ambientes empresariais ocupa cerca de 4x menos espaço e perdendo apenas de 1 a 3% de precisão. Economiza Ram e espaço em disco
        )
        vetor_gerado = resposta_ia['embedding']
        
    except Exception as e:
        # Se a internet falhar ou a IA der erro, avisamos o utilizador
        raise HTTPException(status_code=500, detail=f"Erro ao comunicar com a IA: {str(e)}")

    # 4. Monta o documento com o texto E os números gerados!
    db_document = models.Documents(
        titulo=document.titulo, 
        conteudo=document.conteudo, 
        criado_em=datetime.now(),
        embedding=vetor_gerado # <-- O CÉREBRO MATEMÁTICO ENTRA AQUI!
    )
    
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    return db_document

#Rota de teste antiga
@app.get("/")
def read_root():
    return{"mensagem": "Servidor rodando perfeitamente no Docker!"}