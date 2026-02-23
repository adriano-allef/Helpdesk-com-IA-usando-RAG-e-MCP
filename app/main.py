from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError # <-- O capturador de erros do banco 

#Importações das pastas
from database.database import engine, SessionLocal
from models.models import Base
import models.models as models #para usar o models.User
import schemas.schemas as schemas # Para usar schemas.UserCreate


# 2. O camando do SQLAlchemy:
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

#Rota de teste antiga
@app.get("/")
def read_root():
    return{"mensagem": "Servidor rodando perfeitamente no Docker!"}