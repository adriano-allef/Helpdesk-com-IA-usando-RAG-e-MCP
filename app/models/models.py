# 1. Importar as ferramentas que definem os tipos de dados
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey

# 2. Importar a 'Base' (Ela vem do nosso arquivo conexão)
# É ela que avisa o banco para transformas em uma tabela

from database.database import Base

# 3. Criar a Classe, herdando da Base

class User(Base):
    # 4. Batizar a tabela no banco de dados (o nome deve ser no plural)
    __tablename__ = "users"

    #5. Desenhar as colunas
    id = Column(Integer, primary_key=True, index=True)# configurando o id da tabela
    nome = Column(String, nullable=False)# nulltable=False é o not null do SQL
    email = Column(String, unique=True, nullable=False)
    papel = Column(String, nullable=False)

class Documents(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    conteudo = Column(Text, nullable=False)
    criado_em = Column(DateTime, nullable=False)

class Tickets(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("users.id"))
    titulo = Column(String, nullable=False)
    descricao = Column(Text, nullable=False)
    status = Column(String, nullable=False)
    criado_em = Column(DateTime, nullable=False)