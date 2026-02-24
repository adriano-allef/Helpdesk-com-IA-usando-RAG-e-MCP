import os
import google.generativeai as genai
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
import models.models as models
import schemas.schemas as schemas

router = APIRouter(prefix="/chat", tags=["Assistente Virtual (RAG)"])

@router.post("/", response_model=schemas.ChatResponse)
def chat_with_bot(query: schemas.ChatRequest, db: Session = Depends(get_db)):
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

        documento_encontrado = db.query(models.Documents).order_by(
            models.Documents.embedding.cosine_distance(vetor_pergunta)
        ).first()

        if not documento_encontrado:
            return {"resposta": "Desculpe, não tenho nenhum manual cadastrado ainda."}
        
        prompt_invisivel = f"""
        Você é uma assistente virtual corporativo de Helpdesk, muito educado e prestativo.
        O seu trabalho é responder à dúvida do utilizador usando EXCLUSIVAMENTE o documento oficial abaixo.
        Se a resposta não estiver no documento, diga educadamente que não tem essa informação.
        Não invente dados, se não tiver todas as informações, dê apenas as informações do documento e complemente dizendo a frase a seguir no tom da conversa: sou um assistente corporativo seguro, se eu disser algo a mais, estarei inventando informações, meu conhecimento se limita aos manuais da minha base de dados.
        
        SE NÃO TIVER NENHUMA RESPOSTA NOS MANUAIS(adapte para o tom da conversa.): 
        Não tenho a resposta para isso no momento e ja estou encaminhando um alerta para que a área responsável atualize os manuais.

        HISTÓRICO RECENTE DA CONVERSA:
        {query.historico}

        DOCUMENTO OFICIAL DA EMPRESA:
        Título: {documento_encontrado.titulo}
        Conteúdo: {documento_encontrado.conteudo}

        DÚVIDA DO UTILIZADOR:
        {query.pergunta}
        """

        modelo_chat = genai.GenerativeModel('gemini-2.5-flash')
        resposta_final = modelo_chat.generate_content(prompt_invisivel)

        return {"resposta": resposta_final.text}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno no Chatbot: {str(e)}")