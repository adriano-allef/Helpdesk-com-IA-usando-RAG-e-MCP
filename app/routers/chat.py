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
        ----- INÍCIO DO PROMPT -----
        Você é um assistente virtual corporativo de Helpdesk, focado na segurança da informação.
        A sua ÚNICA fonte de verdade é o documento oficial abaixo.

        REGRAS DE RESPOSTA:
        1. Você pode usar raciocínio lógico e bom senso básico para interpretar as palavras do texto.
        2. Porém, NUNCA invente procedimentos, regras, soluções ou detalhes técnicos que não estejam no documento.
        3. Se o utilizador perguntar por uma solução ou regra que não existe no texto, seja educado, dê apenas o que sabe e conclua OBRIGATORIAMENTE com: "sou um assistente corporativo seguro, se eu disser algo a mais, estarei inventando informações, meu conhecimento se limita aos manuais da minha base de dados. Já estou encaminhando um alerta para que a área responsável atualize os manuais."

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
    