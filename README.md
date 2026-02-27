# 🤖 Helpdesk AI: RAG & Agentic Workflow

## 🎯Sobre o Projeto
 
 Este projeto implementa uma arquitetura de RAG (Retrieval-Augmented Generation) focada em resolver o problema de alucinação em LLMs para uso corporativo.
 
 O objetivo é criar um Assistente de Helpdesk que consulta manuais internos e responde de forma técnica e precisa. Caso a solução não esteja na base de dados, o sistema utiliza um fluxo agêntico para abrir um ticket automaticamente no Trello via n8n, garantindo que o usuário nunca fique sem suporte.
 
 A infraestrutura foi desenvolvida via código (`FastAPI`) para assegurar total controle sobre o fluxo de dados, segurança e custos de API.
 
 ## 💡O que ele fazBusca 
 
 * **Vetorial (pgvector):** Realiza busca semântica em documentos, encontrando o contexto correto em vez de apenas palavras-chave.
 * **Filtro de Respostas (Groundedness):** Configuração de prompt para garantir que a IA responda apenas o que consta nos documentos oficiais. 
 * **Automação de Tickets (n8n):** Se a IA não souber a resposta, ela dispara um Webhook para o `n8n`, que cria um card no `Trello` da equipe de suporte.
 * **Histórico de Chat:** Gerenciamento de memória no frontend para manter o fluxo da conversa.
 
## 🛠️ Stack Tecnológico

* **Backend:**
Python + FastAPI + SQLAlchemy
* **Base de Dados:** PostgreSQL com extensão ´pgvector´
* **Inteligência Artificial:** Google Gemini API (Embeddings e LLM)
* **Orquestração:** n8n e Trello 
* **APIFrontend:** Streamlit

## 🧠 Escolhas Técnicas e Arquitetura
O sistema foi estruturado com foco em performance e segurança. Abaixo, os pontos principais:
1. **Performance de Vetores (768 dimensões):**  
Configurei a saída do modelo de embeddings para __768 dimensões__ (em vez de 3072). Isso reduz o consumo de memória do banco e acelera a busca por similaridade sem perda de precisão no contexto de helpdesk.
2. **Controle de Respostas (Strict Groundedness):** 
O prompt atua em modo restrito. Se a informação não existir nos manuais, o modelo informa o limite do seu conhecimento e sugere a abertura do ticket.
3. **Gatilhos de Automação:** 
Quando a IA não encontra a resposta, ela insere uma tag invisível no backend. O FastAPI intercepta essa tag, limpa o texto para o usuário e dispara um __Webhook assíncrono__    para o n8n.
4. **Segurança DevSecOps:** 
Gestão de credenciais via arquivos .env injetados nos contêineres e uso do cofre de segredos (Vault) nativo do n8n.
5. **Organização do Código (Clean Architecture):** Uso do `APIRouter` para separar as lógicas de usuários, documentos e chat em módulos independentes.

## 🚀 Como Executar o Projeto
Pré-requisitos
* Docker e Docker Compose instalados.
* Chave de API do Google AI Studio.
Passo a Passo
1. Clone o repositório:
    ```bash
    git clone https://github.com/adriano-allef/Helpdesk-com-IA-usando-RAG-e-MCP.gitcd Helpdesk-com-IA-usando-RAG-e-MCP
    ```
2. Configure as variáveis de ambiente:

    Crie um arquivo `.env` na raiz com:
    ```.env
    GEMINI_API_KEY=sua_chave_aqui
    POSTGRES_USER=admin
    POSTGRES_PASSWORD=senha_segura
    POSTGRES_DB=helpdesk_db
    ```
    3. Suba a infraestrutura:
    ```bash
    docker compose up --build -d
    ```

    4. Inicie o Frontend:
    ``` bash
    pip install -r requirements.txt
    streamlit run frontend.py
    ```
## 📡 Endpoints da API
| Rota | Método | Descrição |
| :--- | :--- | :--- |
| `/users/` | `POST` | Cadastro de novos usuários. |
| `/documents/` | `POST` |Vetorização e armazenamento de manuais |
| `/documents/search` | `POST` | Teste de busca semântica por similaridade.(`pgvector`). |
| `/chat/` | `POST` | Motor RAG principal e disparo de gatilhos. |

📂 Estrutura de Pastas
```plaintext
app/
├── database/
│   └── database.py      # Conexão e sessão do banco de dados
├── models/
│   └── models.py        # Tabelas SQLAlchemy (ORM)
├── routers/
│   ├── chat.py          # Lógica RAG e Prompts
│   ├── documents.py     # Lógica de Embeddings
│   └── users.py         # Lógica de Usuários
├── schemas/
│   └── schemas.py       # Validação de dados (Pydantic)
├── main.py              # Ponto de entrada da API FastAPI
├── docker-compose.yml   # Orquestração dos contêineres (Docker)
├── Dockerfile           # Imagem do Backend
├── frontend.py          # Interface do usuário com Streamlit
├── requirements.txt     # Dependências do projeto
└── README.md            # Documentação (Você está aqui!)
```
## 🔮 Roadmap Concluído
* [x] Integração com banco vetorial (pgvector).
* [x] Memória conversacional no frontend.
* [x] Agentic Workflow: Disparo de Webhooks para n8n.
* [x] Integração Trello: Criação de cards automática.
* [x] Dashboard Visual: Timeline de arquitetura no Streamlit.