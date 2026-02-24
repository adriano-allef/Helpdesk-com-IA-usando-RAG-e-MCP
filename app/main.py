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

@app.post("/documents/search", response_model=list[schemas.DocumentResponse])
def search_documents(query: schemas.SearchQuery, db: Session = Depends(get_db)):
    #1. Valida a chave da IA
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise HTTPException(status_code=500, detail="Chave da IA não configurada.")
    
    genai.configure(api_key=gemini_key)

    try:
        #2. Transforma a Pergunta num vetor
        resposta_ia = genai.embed_content(
            model="models/gemini-embedding-001",
            content=query.pergunta,
            task_type="retrieval_query", # <-- Avia a IA que isso é uma pergunta.
            output_dimensionality=768
        )
        vetor_pergunta = resposta_ia['embedding']
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na IA: {str(e)}")
    
    # 3. Busca vetorial no Postgresql
    # Pedi ao banco para ordenar os documentos calculando a distancia matemática
    # entre o vetor do documento e o vetor da pergunta
    resultados = db.query(models.Documents).order_by(
        models.Documents.embedding.cosine_distance(vetor_pergunta)
    ).limit(2).all() # limit(2) traz apenas os 2 manuais mais relevantes

    return resultados

@app.post("/chat", response_model=schemas.ChatResponse)
def chat_with_bot(query: schemas.SearchQuery, db: Session = Depends(get_db)):
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise HTTPException(status_code=500, detail="Chave da IA não configurada.")
    
    genai.configure(api_key=gemini_key)

    try:
        #---PARTE 1: O RETRIEVAL (A Busca Vetorial) ---
        #transforma a pergunta em vetor
        resposta_ia = genai.embed_content(
            model="models/gemini-embedding-001",
            content=query.pergunta,
            task_type="retrieval_query",
            output_dimensionality=768
        )
        vetor_pergunta = resposta_ia['embedding']

        # Procura o documento MAIS RELEVANTE (pega apenas o 1° colocado com .firts())
        documento_encontrado = db.query(models.Documents).order_by(
            models.Documents.embedding.cosine_distance(vetor_pergunta)
        ).first()

        #Se o banco tiver vazio, avisa o utilizador
        if not documento_encontrado:
            return {"resposta": "Desculpe, não tenho nenhum manual cadastrado ainda."}
        
        #---Parte 2: A Generation (A Engenharia de Prompt)---
        #Montei um texto invisível dando ordens estritas à IA
        prompt_invisivel = f"""
        Você é uma assistente virtual corporativo de Helpdesk, muito educado e prestativo.
        O seu trabalho é responder à dívida do utilizador usando EXCLUSIVAMENTE o documento oficial abaixo.
        Se a resposta não estiver no documento, diga educadamente que não tem essa informação.
        Não invente dados, se não tiver todas as informações, dê apenas as informações do documento e complemente dizendo a frase a seguir no tom da conversa: sou um assistente corporativo seguro, se eu disser algo a mais, estarei inventando informações, meu conhecimento se limita aos manuais da minha base de dados.
        
        SE NÃO TIVER NENHUMA RESPOSTA NOS MANUAIS(adapte para o tom da conversa.): 
        Não tenho a resposta para isso no momento e ja estou encaminhando um alerta para que a área responsável atualize os manuais.

        DOCUMENTO OFICIAL DA EMPRESA:
        Título: {documento_encontrado.titulo}
        Conteúdo: {documento_encontrado.conteudo}

        DÚVIDA DO UTILIZADOR:
        {query.pergunta}
        """

        #Invoquei o modelo conversacional rápido do Google (Flash)
        modelo_chat = genai.GenerativeModel('gemini-2.5-flash')
        resposta_final = modelo_chat.generate_content(prompt_invisivel)

        # Devolvemos a resposta processada para a tela
        return {"resposta": resposta_final.text}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno no Chatbot: {str(e)}")

#Rota de teste antiga
@app.get("/")
def read_root():
    return{"mensagem": "Servidor rodando perfeitamente no Docker!"}