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

# --- 2. FUNÇÃO ANIMAÇÃO (SEGURANÇA TOTAL) ---
def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else None
    except: return None

lottie_anim = load_lottieurl("https://lottie.host/573612d1-2905-4927-9976-f3689c177b96/K2p27X9Rz8.json")

# --- 3. CSS PARA MOLDURA 3D E COR DOS TÍTULOS DOS CAMPOS (VERDE LOGO) ---
st.markdown("""
    <style>
    .stApp { background-color: #f1f5f9; }
    
    /* Forçar a cor Verde da Logo (#007a7c) nos labels de input */
    div[data-testid="stForm"] label,
    div[data-testid="stWidgetLabel"] label,
    .stTextInput label,
    .stSelectbox label {
        color: #007a7c !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
    }
    
    /* Moldura 3D Premium Neumórfica */
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
        color: #007a7c !important;
        font-size: 3.5rem !important;
        font-weight: 900 !important;
        letter-spacing: -1px;
        margin: 0 !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.05);
    }
    
    .subtitulo-principal {
        color: #64748b !important;
        font-size: 1.3rem !important;
        font-weight: 500;
        margin-top: 10px;
    }
    
    .stButton>button {
        background-color: #007a7c !important;
        color: white !important;
        border-radius: 10px;
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

@st.cache_data(ttl=300)
def buscar_dados(aba_index):
    try:
        gc = conecta_planilha()
        if gc:
            df = pd.DataFrame(gc.get_worksheet(aba_index).get_all_records())
            return df
        return pd.DataFrame()
    except: return pd.DataFrame()

# --- 5. INTERFACE ---
def main():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    with st.sidebar:
        # Tenta carregar a logo na lateral (usando caminho relativo se estiver no GitHub)
        if os.path.exists("logo.jpg"): 
            st.image("logo.jpg", use_container_width=True)
        else:
            st.markdown("<h2 style='text-align:center;'>🏢 ImobIJX</h2>", unsafe_allow_html=True)
            
        st.divider()
        if st.session_state["password_correct"]:
            st.markdown(f"👤 **{st.session_state['user_logado'].upper()}**")
            menu = st.radio("SISTEMA MASTER", ["🏛️ Dashboard", "🔥 Zonas de Calor", "🤝 CRM Clientes", "📄 Banco Talentos"])
            if st.button("🚪 Sair"):
                st.session_state["password_correct"] = False
                st.rerun()
        else:
            menu = st.radio("MENU PÚBLICO", ["🏠 Início", "🎯 Trabalhe Conosco", "🔐 Acesso Master"])

    # --- 6. CONTEÚDO CENTRAL ---
    if st.session_state["password_correct"]:
        # Telas Privadas (Mateus, Janeide, Gessica)
        if menu == "🏛️ Dashboard":
            df_clientes = buscar_dados(3)
            # Moldura 3D com o Nome da Empresa
            st.markdown(f'''
                <div class="moldura-3d">
                    <h1 class="titulo-principal">Janeide Xavier LTDA</h1>
                    <p class="subtitulo-principal">Painel Master de Inteligência Imobiliária</p>
                </div>
            ''', unsafe_allow_html=True)
            st.success(f"Logado como: {st.session_state['user_logado'].capitalize()}")
            # ... resto do dashboard ...

        elif menu == "🤝 CRM Clientes":
            st.title("🤝 Gestão de Clientes")
            df_clientes = buscar_dados(3)
            st.dataframe(df_clientes, use_container_width=True)

        elif menu == "📄 Banco Talentos":
            st.title("📄 Currículos Recebidos")
            df_talentos = buscar_dados(2)
            st.dataframe(df_talentos, use_container_width=True)
        # ... outras telas ...

    else:
        # TELAS PÚBLICAS
        if menu == "🏠 Início":
            st.markdown(f'''
                <div class="moldura-3d">
                    <h1 class="titulo-principal">Janeide Xavier LTDA</h1>
                    <p class="subtitulo-principal">Transformando dados em lares em Feira de Santana</p>
                </div>
            ''', unsafe_allow_html=True)
            
            if lottie_anim:
                st_lottie(lottie_anim, height=350, key="home_anim")
            
        elif menu == "🎯 Trabalhe Conosco":
            st.markdown('<div class="moldura-3d"><h1 class="titulo-principal">Trabalhe Conosco</h1></div>', unsafe_allow_html=True)
            with st.container():
                st.write("### Faça parte do nosso time de elite")
                with st.form("cv_recrutamento"):
                    nome = st.text_input("Nome Completo")
                    zap = st.text_input("WhatsApp (com DDD)")
                    link = st.text_input("Link do LinkedIn ou Currículo")
                    if st.form_submit_button("Enviar Candidatura"):
                        gc = conecta_planilha()
                        if gc:
                            gc.get_worksheet(2).append_row([datetime.now().strftime('%d/%m/%Y'), nome, zap, "Candidato", link])
                            st.success("Candidatura enviada com sucesso!")

        elif menu == "🔐 Acesso Master":
            st.markdown('<div class="moldura-3d"><h1 class="titulo-principal">Login Master</h1></div>', unsafe_allow_html=True)
            with st.container():
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
                    except: st.error("Erro na configuração de usuários (Secrets).")

    st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 11px; margin-top:100px;'>© 2026 Imobiliária Janeide Xavier LTDA</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
