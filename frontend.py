import streamlit as st
import requests

with st.sidebar:
    st.markdown("### Arquitetura do Sistema")
    st.markdown("---")
    
    # Criamos o estilo CSS e a estrutura HTML da linha do tempo
    fluxograma_html = """
    <style>
    .timeline { 
        border-left: 2px solid #4a90e2; 
        padding-left: 15px; 
        margin-left: 10px; 
        font-family: sans-serif;
    }
    .step { 
        margin-bottom: 25px; 
        position: relative;
    }
    .step::before {
        content: '';
        position: absolute;
        left: -21px;
        top: 5px;
        width: 10px;
        height: 10px;
        background-color: #4a90e2;
        border-radius: 50%;
    }
    .step b { 
        font-size: 1.05em; 
    }
    .step p { 
        margin: 5px 0 0 0; 
        font-size: 0.9em; 
        opacity: 0.8; 
        line-height: 1.4;
    }
    </style>
    
    <div class="timeline">
        <div class="step">
            <b>1. Entrada do Usuário</b>
            <p>Recebimento do problema via chat.</p>
        </div>
        <div class="step">
            <b>2. Motor de Busca (RAG)</b>
            <p>Varredura nos manuais técnicos da base de conhecimento.</p>
        </div>
        <div class="step">
            <b>3. Tomada de Decisão (IA)</b>
            <p><b>Solução encontrada:</b> Responde ao usuário.<br>
            <b>Sem solução:</b> Aciona orquestração.</p>
        </div>
        <div class="step">
            <b>4. Orquestração (n8n)</b>
            <p>Captura dos dados via Webhook em segundo plano.</p>
        </div>
        <div class="step">
            <b>5. Persistência e Fila</b>
            <p>• Gravação na tabela tickets (PostgreSQL).<br>
            • Criação de Card no Kanban (Trello).</p>
        </div>
    </div>
    """
    
    # O unsafe_allow_html=True permite renderizar o CSS/HTML no Streamlit
    st.markdown(fluxograma_html, unsafe_allow_html=True)
    
    st.markdown("---")
    st.caption("Tech Stack: Python • Docker • n8n • PostgreSQL")
# Configuração da página
st.set_page_config(page_title="Helpdesk IA", page_icon="🤖")
st.title("🤖 Assistente Virtual de Manuais")
st.caption("Respostas precisas e fundamentadas diretamente nos manuais da instituição.")

# 1. Inicializa o histórico de chat na memória do Streamlit
if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

# 2. Mostra as mensagens antigas na tela (para parecer um chat real)
for msg in st.session_state.mensagens:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 3. Caixa de texto para o utilizador digitar a pergunta
pergunta = st.chat_input("Digite a sua dúvida (ex: Como redefinir a password?)")

if pergunta:
    # Mostra a pergunta do utilizador na tela e guarda no histórico
    with st.chat_message("user"):
        st.markdown(pergunta)
    st.session_state.mensagens.append({"role": "user", "content": pergunta})

    # Mostra o balão do assistente a "pensar"
    with st.chat_message("assistant"):
        with st.spinner("A consultar os manuais da empresa..."):
            try:
                # 4. Faz a chamada HTTP para o seu backend (FastAPI)
                # NOTA: O endereço deve bater com o local onde a sua API está a correr
                url_api = "http://localhost:8000/chat"

                # Pegamos as últimas 4 mensagens do histórico para a IA ter contexto
                historico_recente = st.session_state.mensagens[-4:] if len(st.session_state.mensagens) > 0 else []
                
                resposta = requests.post(url_api, json={"pergunta": pergunta,
                "historico": historico_recente
                })
                
                if resposta.status_code == 200:
                    texto_resposta = resposta.json()["resposta"]
                    st.markdown(texto_resposta)
                    # Guarda a resposta no histórico
                    st.session_state.mensagens.append({"role": "assistant", "content": texto_resposta})
                else:
                    st.error(f"Erro na API: {resposta.status_code}")
                    st.write(resposta.text)
                    
            except requests.exceptions.ConnectionError:
                st.error("Erro de conexão. O servidor FastAPI (Docker) está a correr?")