import streamlit as st
import os
import json
from dotenv import load_dotenv
import requests

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
modelo = "gpt-4.1"
HIST_FILE = "historico.json"

USUARIOS = {
    "usuario1": "senha123",
    "admin": "admin123"
}

def carregar_historico():
    if os.path.exists(HIST_FILE):
        with open(HIST_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def salvar_historico(historico):
    with open(HIST_FILE, "w", encoding="utf-8") as f:
        json.dump(historico, f, ensure_ascii=False, indent=2)

def enviar_pergunta():
    pergunta = st.session_state.pergunta.strip()
    if pergunta == "":
        st.warning("Digite uma pergunta antes de enviar!")
        return
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": modelo,
        "messages": [{"role": "user", "content": pergunta}],
        "max_tokens": 1024,
        "temperature": 0.7
    }
    resposta = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    resposta_json = resposta.json()
    
    if resposta.status_code == 200:
        resposta_texto = resposta_json['choices'][0]['message']['content']
        
        st.session_state.historico.append({
            "pergunta": pergunta,
            "resposta": resposta_texto
        })
        salvar_historico(st.session_state.historico)
        
        st.session_state.selecionado = len(st.session_state.historico) - 1
        st.session_state.pergunta = ""
    else:
        st.error(f"Erro na API: {resposta_json}")

# Inicializa variáveis de estado se não existirem
if "logado" not in st.session_state:
    st.session_state["logado"] = False

if "usuario" not in st.session_state:
    st.session_state["usuario"] = ""

if "login_usuario" not in st.session_state:
    st.session_state["login_usuario"] = ""

if "login_senha" not in st.session_state:
    st.session_state["login_senha"] = ""

def mostrar_login():
    st.title("Login")
    st.session_state.login_usuario = st.text_input("Usuário", value=st.session_state.login_usuario)
    st.session_state.login_senha = st.text_input("Senha", type="password", value=st.session_state.login_senha)

    if st.button("Entrar"):
        usuario = st.session_state.login_usuario
        senha = st.session_state.login_senha
        if usuario in USUARIOS and USUARIOS[usuario] == senha:
            st.session_state["logado"] = True
            st.session_state["usuario"] = usuario
            # Limpa os campos de login
            st.session_state.login_usuario = ""
            st.session_state.login_senha = ""
        else:
            st.error("Usuário ou senha incorretos")

def mostrar_app():
    # Inicializa histórico, pergunta e seleção após login
    if "historico" not in st.session_state:
        st.session_state.historico = carregar_historico()

    if "pergunta" not in st.session_state:
        st.session_state.pergunta = ""

    if "selecionado" not in st.session_state:
        st.session_state.selecionado = None

    st.sidebar.title(f"Olá, {st.session_state['usuario']}!")
    if st.sidebar.button("Sair"):
        st.session_state["logado"] = False
        st.session_state["usuario"] = ""
        # Não precisa de st.experimental_rerun, só volta a mostrar a tela de login na próxima execução

    st.sidebar.title("Histórico")
    for i, item in enumerate(st.session_state.historico):
        preview = " ".join(item["pergunta"].split()[:10])
        if len(item["pergunta"].split()) > 10:
            preview += "..."
        if st.sidebar.button(preview, key=f"btn_{i}"):
            st.session_state.selecionado = i

    st.title("Assistente GPT")
    st.write("Faça uma pergunta e eu responderei!")

    with st.form("form_pergunta", clear_on_submit=False):
        st.text_area("Pergunta:", key="pergunta", height=150)
        st.form_submit_button("Enviar", on_click=enviar_pergunta)

    st.markdown("---")

    if st.session_state.selecionado is not None:
        item = st.session_state.historico[st.session_state.selecionado]

        with st.chat_message("user"):
            st.markdown(item["pergunta"])

        with st.chat_message("assistant"):
            st.markdown(item["resposta"])
    else:
        st.info("Nenhuma pergunta selecionada no histórico.")

# Fluxo principal
if not st.session_state["logado"]:
    mostrar_login()
else:
    mostrar_app()