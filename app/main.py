from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

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
def creae_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    # 1. Tradução: Peguei os dados validadeos pelo Pydantic (user)
    # e transformei no formato que o SQLALchemy entende (models.User)
    db_user = models.User(nome=user.nome, email=user.email, papel=user.papel)

    #2. Adicionei o novo usuario na sessão do banco
    db.add(db_user)

    #3. Executei o "Salvar" de fato (isso gera o ID automaticamente)
    db.commit()

    #4. Atualizei a variavel com os dados novos do banco ()
    db.refresh(db_user)

    #5.Devolvo o usuario (O Pydantic vai pegar isso e transformar em JSON graças àquele from_attributes=True!)
    return db_user

#Rota de teste antiga
@app.get("/")
def read_root():
    return{"mensagem": "Servidor rodando perfeitamente no Docker!"}