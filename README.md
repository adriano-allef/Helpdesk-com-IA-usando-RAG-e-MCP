# 🤖 Assistente Virtual Corporativo (RAG & MCP Ready)

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-336791.svg)
![Gemini](https://img.shields.io/badge/Gemini-2.5_Flash-orange.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-FF4B4B.svg)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)

## 🎯 Sobre o Projeto
Um dos maiores receios das empresas na adoção de Inteligência Artificial é a "alucinação" — o risco de o modelo inventar regras ou procedimentos corporativos que não existem. Para resolver este problema prático, desenvolvi do zero uma arquitetura **RAG (Retrieval-Augmented Generation)** focada em segurança, governança e fidelidade aos dados (*Strict Groundedness*).

O meu projeto é um **Assistente Virtual de Helpdesk** desenhado para consultar manuais internos de uma instituição e responder aos utilizadores com precisão cirúrgica. Em vez de utilizar ferramentas *no-code*, decidi construir toda a infraestrutura para garantir o controlo total sobre o fluxo de dados, a segurança e os custos computacionais.

## 💡 Principais Funcionalidades
- **Busca Semântica Avançada:** Vetorização de documentos para encontrar a resposta exata baseada no contexto, e não apenas em palavras-chave.
- **Memória Conversacional:** O *frontend* gere o histórico recente, permitindo ao utilizador fazer perguntas de acompanhamento (ex: "E onde fica essa bandeja?") sem perder o contexto.
- **Zero Alucinação (Trava de Segurança):** Se a resposta não estiver explicitamente na base de dados, a IA recusa-se a inventar, assumindo uma postura corporativa e transparente.

## 🛠️ Stack Tecnológico
- **Backend:** Python + FastAPI + SQLAlchemy
- **Base de Dados:** PostgreSQL com extensão `pgvector`
- **Inteligência Artificial:** API do Google (Embeddings `gemini-embedding-001` e LLM `gemini-2.5-flash`)
- **Frontend:** Streamlit
- **Infraestrutura:** Docker & Docker Compose

## 🧠 Decisões Arquiteturais e Destaques
Desenvolvi este sistema com mentalidade de ambiente de produção. Destaco 4 grandes decisões arquiteturais:

### 1. Otimização de Recursos (Redução de Custos e RAM)
Em vez de utilizar a dimensionalidade padrão de 3072 do modelo de *embeddings* do Google, **forcei a saída para 768 dimensões**. Esta decisão reduziu drasticamente o consumo de memória RAM do servidor e o armazenamento na base de dados, mantendo a precisão da busca semântica por *Cosine Distance*.

### 2. Strict Groundedness (Fidelidade aos Dados)
Através de Engenharia de Prompt focada, blindei a IA. Se um utilizador perguntar algo fora dos manuais, o modelo ativa um protocolo de segurança, informando que o seu conhecimento está restrito à base oficial, eliminando o risco de *compliance*.

### 3. Preparado para Escalar (MCP Ready)
Programei a IA para, ao não encontrar uma resposta, gerar um gatilho em linguagem natural: *"Já estou a encaminhar um alerta para que a área responsável atualize os manuais"*. Este comportamento foi desenhado propositadamente para uma futura integração com o **Model Context Protocol (MCP)**, permitindo que a IA abra *tickets* no Jira de forma autónoma no futuro.

### 4. Clean Architecture
Refatorei e modularizei a API utilizando o `APIRouter` do FastAPI. As responsabilidades estão claramente separadas (*Separation of Concerns*): gestão de utilizadores, vetorização de documentos e motor do *chatbot* funcionam em módulos independentes, facilitando a manutenção e escalabilidade da aplicação.

## 🚀 Como Executar o Projeto

### Pré-requisitos
- Docker e Docker Compose instalados na sua máquina.
- Uma chave de API válida do [Google AI Studio](https://aistudio.google.com/).

### Passo a Passo
1. Clone este repositório:
   ```bash
   git clone [https://github.com/adriano-allef/Helpdesk-com-IA-usando-RAG-e-MCP.git](https://github.com/adriano-allef/Helpdesk-com-IA-usando-RAG-e-MCP.git)
   cd Helpdesk-com-IA-usando-RAG-e-MCP
   ```
2. Crie um ficheiro .env na raiz do projeto e insira a sua chave de API:

    ```bash
    GEMINI_API_KEY=sua_chave_aqui_gerada_no_google_ai_studio
    ```
3. Suba a infraestrutura completa (Base de Dados + API) através do Docker:

    ```bash
    docker-compose up --build
    ```

4. Num terminal separado, inicie o frontend interativo do Streamlit:
    ```bash
    streamlit run frontend.py
    ```

### Acessos Loccais
- Frontend (Chat)
    ```
    http://localhost:8501
    ```

- Documentação da API (Swagger) 
    ```
    http://localhost:8000/docs
    ```

## 📡 Endpoints da API

    
| Rota | Método | Descrição |
| :--- | :--- | :--- |
| `/users/` | `POST` | Criação de novos utilizadores. |
| `/documents/` | `POST` | Vetoriza e guarda um novo manual/documento. |
| `/documents/search` | `POST` | Rota de teste para a busca semântica (`pgvector`). |
| `/chat/` | `POST` | Motor principal do RAG. Recebe a pergunta e o histórico, e devolve a resposta gerada. |

## 📂 Estrutura de Ficheiros

```plaintext
app/
├── database/
│   └── database.py      # Ligação e sessão da base de dados
├── models/
│   └── models.py        # Tabelas SQLAlchemy (ORM)
├── routers/
│   ├── chat.py          # Lógica RAG e Prompts
│   ├── documents.py     # Lógica de Embeddings
│   └── users.py         # Lógica de Utilizadores
├── schemas/
│   └── schemas.py       # Validação de dados (Pydantic)
├── main.py              # Orquestrador da API FastAPI
├── docker-compose.yml   # Orquestração dos contentores
├── Dockerfile           # Imagem do Backend
├── frontend.py          # UI com Streamlit
├── requirements.txt     # Dependências do projeto
└── README.md            # Documentação (Você está aqui!)
```

## 🔮 Próximos Passos (Roadmap)

- [x] Integração completa com base de dados vetorial.
- [x] Implementação de memória conversacional.
- [ ] **Integração MCP (Model Context Protocol)**: Ligar o gatilho de texto a uma função real que crie *tickets* em ferramentas de gestão (Jira/Trello).
- [ ] Criação de interface para carregamento de PDFs (extração de texto e *chunking* dinâmico).