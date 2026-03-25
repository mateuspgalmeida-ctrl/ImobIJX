import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import requests
from streamlit_lottie import st_lottie
import os

# --- 1. CONFIGURAÇÃO DE PÁGINA ---
st.set_page_config(page_title="ImobIJX | Master Intelligence", layout="wide", page_icon="🏢")

# --- 2. FUNÇÃO ANIMAÇÃO ---
def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else None
    except: return None

lottie_anim = load_lottieurl("https://lottie.host/573612d1-2905-4927-9976-f3689c177b96/K2p27X9Rz8.json")

# --- 3. CSS GLOBAL (CORREÇÃO DE CORES E CONTRASTE) ---
st.markdown("""
    <style>
    /* Fundo do App */
    .stApp { background-color: #f1f5f9; }
    
    /* TEXTOS GERAIS (VERDE LOGO) */
    h1, h2, h3, p, span, label {
        color: #007a7c !important;
        font-family: 'Inter', sans-serif;
    }
    
    /* Moldura 3D Neumórfica */
    .moldura-3d {
        background: #f1f5f9;
        padding: 40px;
        border-radius: 30px;
        box-shadow: 20px 20px 60px #d1d5db, -20px -20px 60px #ffffff;
        border: 1px solid rgba(255,255,255,0.2);
        text-align: center;
        margin: 40px auto;
        max-width: 900px;
    }
    
    .titulo-principal {
        font-size: 3.5rem !important;
        font-weight: 900 !important;
        letter-spacing: -1px;
        margin: 0 !important;
    }
    
    /* --- CORREÇÃO DOS CAMPOS DE DIGITAÇÃO (TEXTO BRANCO) --- */
    input {
        color: white !important; /* Cor do texto ao digitar */
        -webkit-text-fill-color: white !important; /* Garante no Chrome/Safari */
    }
    
    /* Garante que o texto dentro de áreas de texto também seja branco */
    div[data-baseweb="input"] {
        color: white !important;
    }

    /* --- CORREÇÃO DOS BOTÕES --- */
    .stButton>button {
        background-color: #007a7c !important;
        color: white !important;
        border-radius: 10px;
        font-weight: bold !important;
        width: 100%;
        border: none;
        padding: 10px;
        transition: 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #005a5c !important;
        color: white !important;
    }

    /* Força o texto branco dentro do botão (evita conflito global) */
    .stButton>button div p {
        color: white !important;
    }
    
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNÇÕES DE DADOS ---
@st.cache_resource
def conecta_planilha():
    try:
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], 
                                                     scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])
        return gspread.authorize(creds).open("Dados_ImobIJX")
    except: return None

def buscar_dados(aba_index):
    try:
        gc = conecta_planilha()
        if gc:
            return pd.DataFrame(gc.get_worksheet(aba_index).get_all_records())
        return pd.DataFrame()
    except: return pd.DataFrame()

# --- 5. INTERFACE ---
def main():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    with st.sidebar:
        if os.path.exists("logo.jpg"): 
            st.image("logo.jpg", use_container_width=True)
        st.divider()
        if st.session_state["password_correct"]:
            menu = st.radio("SISTEMA MASTER", ["🏛️ Dashboard", "🤝 CRM Clientes", "📄 Banco Talentos"])
            if st.button("🚪 Sair"):
                st.session_state["password_correct"] = False
                st.rerun()
        else:
            menu = st.radio("MENU PÚBLICO", ["🏠 Início", "🎯 Trabalhe Conosco", "🔐 Acesso Master"])

    # --- 6. CONTEÚDO CENTRAL ---
    if st.session_state["password_correct"]:
        if menu == "🏛️ Dashboard":
            st.markdown('<div class="moldura-3d"><h1 class="titulo-principal">Janeide Xavier LTDA</h1><p>Painel Master de Inteligência</p></div>', unsafe_allow_html=True)
            st.write("### Olá! Bem-vinda ao seu centro de controle.")
    else:
        if menu == "🏠 Início":
            st.markdown(f'''
                <div class="moldura-3d">
                    <h1 class="titulo-principal">Imobiliária Janeide Xavier LTDA</h1>
                    <p style="font-size: 1.5rem; font-weight: 500;">
                        Inteligência imobiliária em Feira de Santana.
                    </p>
                </div>
            ''', unsafe_allow_html=True)
            if lottie_anim: st_lottie(lottie_anim, height=350)
            
        elif menu == "🎯 Trabalhe Conosco":
            st.markdown('<div class="moldura-3d"><h1 class="titulo-principal">Trabalhe Conosco</h1></div>', unsafe_allow_html=True)
            st.write("### Faça parte do nosso time de elite")
            with st.form("cv_recrutamento"):
                nome = st.text_input("Nome Completo", placeholder="Digite seu nome aqui...")
                zap = st.text_input("WhatsApp (com DDD)", placeholder="(75) 99999-9999")
                link = st.text_input("Link do LinkedIn ou Currículo", placeholder="https://...")
                if st.form_submit_button("Enviar Candidatura"):
                    gc = conecta_planilha()
                    if gc:
                        gc.get_worksheet(2).append_row([datetime.now().strftime('%d/%m/%Y'), nome, zap, "Candidato", link])
                        st.success("Candidatura enviada!")

        elif menu == "🔐 Acesso Master":
            st.markdown('<div class="moldura-3d"><h1 class="titulo-principal">Login Master</h1></div>', unsafe_allow_html=True)
            st.write("### Área restrita para gestão")
            u = st.text_input("Usuário").lower().strip()
            p = st.text_input("Senha", type="password")
            if st.button("Acessar Painel"):
                try:
                    users = st.secrets["credentials"]["usernames"]
                    if u in users and p == users[u]:
                        st.session_state["password_correct"] = True
                        st.session_state["user_logado"] = u
                        st.rerun()
                    else: st.error("Acesso não autorizado.")
                except: st.error("Erro nos Secrets.")

    st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 11px; margin-top:100px;'>© 2026 Imobiliária Janeide Xavier LTDA</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
