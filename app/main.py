from fastapi import FastAPI

#Importar os modelos e o motos de conexão
from database.database import engine
from models.models import Base


# 2. O camndo do SQLAlchemy:
# "Olhe para todos os modelos atrelados à Base e crie as tabelas no banco usando este motor"
Base.metadata.create_all(bind=engine)

#Inicializa o aplicativo FastAPI
app = FastAPI(title="Helpdesk Institucional API")

#Cria o primeiro endpoint de teste

@app.get("/")
def read_root():
    return{"mensagem": "Servidor rodando perfeitamente no Docker!"}