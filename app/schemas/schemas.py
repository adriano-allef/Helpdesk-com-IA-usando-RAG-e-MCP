from pydantic import BaseModel

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
        from_atributtes = True