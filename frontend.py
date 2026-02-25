import streamlit as st
import requests

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