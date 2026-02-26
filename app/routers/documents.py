import os
import io
from pypdf import PdfReader
import google.generativeai as genai
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from datetime import datetime
from database.database import get_db
import models.models as models
import schemas.schemas as schemas

router = APIRouter(prefix="/documents", tags=["Documentos (Base de Conhecimento)"])

#Função auziliar para dividir textos grandes em pedaços menores(Chunking)
def chunk_text(text: str, chunk_size: int =1000):
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i + chunk_size])
        return chunks

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

@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Apenas arquivos PDF são permitidos.")
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise HTTPException(status_code=500, detail="Chave da IA não configurada.")
    genai.configure(api_key=gemini_key)

    try:
        #Lê o ficheiro da memória
        conteudo_pdf = await file.read()
        leitor = PdfReader(io.BytesIO(conteudo_pdf))

        texto_completo = ""
        for pagina in leitor.pages:
            texto_extraido = pagina.extract_text()
            if texto_extraido:
                texto_completo += texto_extraido + "/n"

        if not texto_completo.strip():
            raise HTTPException(status_cod=400, detail="O PDF parece estar ou ser uma imagem sem texto.")
        
        # Fatiamento (Chunking): Divide o texto em blocos de 1000 caracteres
        pedacos_texto = chunk_text(texto_completo, chunk_size=1000)
        documentos_salvos = 0

        for indice, pedaco in enumerate(pedacos_texto):
            # Gera o embedding para cada espaço
            resposta_ia = genai.embed_content(
                model="models/gemini-embedding-001",
                content=pedaco,
                task_type="retrieval_document",
                output_dimensionality=768
            )
            vetor_gerado = resposta_ia['embedding']

            # Guarda no banco de dados
            titulo_pedaco = f"{file.filename} - Parte {indice + 1}"
            db_document = models.Documents(
                titulo=titulo_pedaco,
                conteudo=pedaco,
                criado_em=datetime.now(),
                embedding=vetor_gerado
            )
            db.add(db_document)
            documentos_salvos += 1
            
            db.commit()

            return {"mensagem": f"PDF processado com sucesso! {documentos_salvos} blocos de texto foram vetorizados" }
        
    except Exception as e:
        raise HTTPException(staus_code=500, detail=f"Erro ao processar o PDF: {str(e)}")

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