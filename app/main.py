from fastapi import FastAPI

#Inicializa o aplicativo FastAPI
app = FastAPI(title="Helpdesk Institucional API")

#Cria o primeiro endpoint de teste

@app.get("/")
def read_root():
    return{"mensagem": "Servidor rodando perfeitamente no Docker!"}