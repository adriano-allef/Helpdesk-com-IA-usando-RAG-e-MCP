import os
import google.generativeai as genai
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from database.database import get_db
import models.models as models
import schemas.schemas as schemas

router = APIRouter(prefix="/documents", tags=["Documentos (Base de Conhecimento)"])

@router.post("/", response_model=schemas.DocumentResponse)
def create_document(document: schemas.DocumentCreate, db: Session = Depends(get_db)):
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise HTTPException(status_code=500, detail="Chave da IA não configurada.")
    
    genai.configure(api_key=gemini_key)
    try:
        resposta_ia = genai.embed_content(
            model="models/gemini-embedding-001",
            content=document.conteudo,
            task_type="retrieval_document",
            output_dimensionality=768
        )
        vetor_gerado = resposta_ia['embedding']
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na IA: {str(e)}")

    db_document = models.Documents(
        titulo=document.titulo, 
        conteudo=document.conteudo, 
        criado_em=datetime.now(),
        embedding=vetor_gerado
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

@router.post("/search", response_model=list[schemas.DocumentResponse])
def search_documents(query: schemas.SearchQuery, db: Session = Depends(get_db)):
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise HTTPException(status_code=500, detail="Chave da IA não configurada.")
    
    genai.configure(api_key=gemini_key)
    try:
        resposta_ia = genai.embed_content(
            model="models/gemini-embedding-001",
            content=query.pergunta,
            task_type="retrieval_query",
            output_dimensionality=768
        )
        vetor_pergunta = resposta_ia['embedding']
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na IA: {str(e)}")
    
    resultados = db.query(models.Documents).order_by(
        models.Documents.embedding.cosine_distance(vetor_pergunta)
    ).limit(2).all()
    return resultados