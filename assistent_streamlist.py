import streamlit as st
import os
import json
from dotenv import load_dotenv
import requests

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
modelo = "gpt-4.1"
HIST_FILE = "historico.json"

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

# Inicializa session_state
if "historico" not in st.session_state:
    st.session_state.historico = carregar_historico()

if "pergunta" not in st.session_state:
    st.session_state.pergunta = ""

if "selecionado" not in st.session_state:
    st.session_state.selecionado = None  # índice do item selecionado

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
        
        st.session_state.selecionado = len(st.session_state.historico) - 1  # seleciona o último
        st.session_state.pergunta = ""
    else:
        st.error(f"Erro na API: {resposta_json}")

# Sidebar com histórico resumido e seleção
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
    st.text_input("Pergunta:", key="pergunta")
    st.form_submit_button("Enviar", on_click=enviar_pergunta)

st.markdown("---")

# Exibe chat com st.chat_message para conversa selecionada
if st.session_state.selecionado is not None:
    item = st.session_state.historico[st.session_state.selecionado]

    # Mensagem do usuário
    with st.chat_message("user"):
        st.markdown(item["pergunta"])

    # Mensagem do assistente
    with st.chat_message("assistant"):
        st.markdown(item["resposta"])
else:
    st.info("Nenhuma pergunta selecionada no histórico.")