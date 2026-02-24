from pydantic import BaseModel, Field
from datetime import datetime

#1. Schema para criar um produto ( O que o usuário digita no site)
#não tem ID aqui, porque o ID quem cria é o banco de dados depois!

class UserCreate(BaseModel):
    nome: str
    email: str
    papel: str

#2. Schema para DEVELVER um produto (O que a API manda de manda de volta para tela)
# Aqui TEM o ID, porque nós já fomos buscar no banco.

class UserResponse(BaseModel):
    id: int
    nome: str
    email: str
    papel: str

    # Essa configuração extra avisa o Pydantic que ele vai receber os dados de um "Modelo do SQLAlchemy" e não de um simples dicionário.
    class Config:
        from_attributtes = True

class DocumentCreate(BaseModel):
    titulo: str
    conteudo: str

class DocumentResponse(BaseModel):
    id: int
    titulo: str = Field(min_length=1)#não aceita ""
    conteudo: str = Field(min_length=10)#minimo 10 caracteres para o conteudo
    criado_em: datetime

    class Config:
        from_attributes = True

#5. Schema para a requisição de Busca Semântica
class SearchQuery(BaseModel):
    pergunta: str

#6. Schema para devolver a resposta conversacional da IA
class ChatResponse(BaseModel):
    resposta: str

class ChatRequest(BaseModel):
    pergunta: str
    historico: list[dict] = [] # Vai receber as mensagens anteriores