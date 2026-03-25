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

# --- 2. FUNÇÃO ANIMAÇÃO (COM TRAVA DE SEGURANÇA) ---
def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else None
    except: return None

lottie_anim = load_lottieurl("https://lottie.host/573612d1-2905-4927-9976-f3689c177b96/K2p27X9Rz8.json")

# --- 3. CSS PARA FORÇAR VISIBILIDADE DO NOME ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #1e293b; }
    
    /* Forçar o Título a aparecer em Verde Escuro */
    .titulo-principal {
        color: #007a7c !important;
        text-align: center;
        font-size: 3.5rem !important;
        font-weight: 900 !important;
        margin-top: 50px !important;
        margin-bottom: 5px !important;
        display: block !important;
    }
    .subtitulo-principal {
        color: #475569 !important;
        text-align: center;
        font-size: 1.5rem !important;
        font-weight: 500;
        margin-bottom: 40px;
    }
    .mural-master {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        color: #fbbf24; padding: 25px; border-radius: 15px;
        border-left: 8px solid #fbbf24; margin: 20px 0;
    }
    .kpi-card {
        background: #f8fafc; padding: 20px; border-radius: 12px;
        border: 1px solid #e2e8f0; text-align: center; color: #1e293b;
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
        df = pd.DataFrame(gc.get_worksheet(aba_index).get_all_records())
        return df
    except: return pd.DataFrame()

# --- 5. INTERFACE ---
def main():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    with st.sidebar:
        if os.path.exists("logo.jpg"): st.image("logo.jpg")
        st.divider()
        if st.session_state["password_correct"]:
            st.markdown(f"👤 **{st.session_state['user_logado'].upper()}**")
            menu = st.radio("SISTEMA", ["🏛️ Dashboard", "🔥 Zonas de Calor", "🤝 CRM", "📄 Talentos"])
            if st.button("🚪 Sair"):
                st.session_state["password_correct"] = False
                st.rerun()
        else:
            menu = st.radio("NAVEGAÇÃO", ["🏠 Início", "🎯 Trabalhe Conosco", "🔐 Acesso Restrito"])

    # CONTEÚDO CENTRAL
    if st.session_state["password_correct"]:
        df_clientes = buscar_dados(3)
        
        if menu == "🏛️ Dashboard":
            st.markdown('<h1 class="titulo-principal">Imobiliária Janeide Xavier LTDA</h1>', unsafe_allow_html=True)
            st.markdown('<p class="subtitulo-principal">Painel de Controle Estratégico</p>', unsafe_allow_html=True)
            
            st.markdown("""<div class="mural-master"><h3>📢 Mural Master</h3><p>Meta: Dominar o <b>SIM e Noide Cerqueira</b>!</p></div>""", unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f'<div class="kpi-card"><h4>Leads</h4><h2>{len(df_clientes)}</h2></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="kpi-card"><h4>Vendas</h4><h2>Ativas</h2></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="kpi-card"><h4>Foco</h4><h2>VGV Feira</h2></div>', unsafe_allow_html=True)

        elif menu == "🔥 Zonas de Calor":
            st.title("🔥 Zonas de Calor")
            if not df_clientes.empty:
                st.plotly_chart(px.bar(df_clientes['Bairro'].value_counts().reset_index(), x='Bairro', y='count', color='count', color_continuous_scale='OrRd'))

        elif menu == "🤝 CRM":
            st.title("🤝 Gestão de Clientes")
            st.dataframe(df_clientes, use_container_width=True)

        elif menu == "📄 Talentos":
            st.title("📄 Banco de Currículos")
            st.dataframe(buscar_dados(2), use_container_width=True)

    else:
        if menu == "🏠 Início":
            # NOME DA IMOBILIÁRIA SEMPRE VISÍVEL AQUI
            st.markdown('<h1 class="titulo-principal">Imobiliária Janeide Xavier LTDA</h1>', unsafe_allow_html=True)
            st.markdown('<p class="subtitulo-principal">Inovação e Inteligência Imobiliária</p>', unsafe_allow_html=True)
            
            if lottie_anim:
                st_lottie(lottie_anim, height=350, key="main_anim")
            
        elif menu == "🎯 Trabalhe Conosco":
            st.markdown('<h1 class="titulo-principal">Trabalhe Conosco</h1>', unsafe_allow_html=True)
            with st.form("cv_form"):
                n = st.text_input("Nome Completo")
                w = st.text_input("WhatsApp")
                l = st.text_input("Link do Currículo/LinkedIn")
                if st.form_submit_button("Enviar Candidatura"):
                    gc = conecta_planilha()
                    if gc:
                        gc.get_worksheet(2).append_row([datetime.now().strftime('%d/%m/%Y'), n, w, "Interessado", l])
                        st.success("Enviado com sucesso!")

        elif menu == "🔐 Acesso Restrito":
            st.markdown('<h1 class="titulo-principal">Login Master</h1>', unsafe_allow_html=True)
            u = st.text_input("Usuário").lower().strip()
            p = st.text_input("Senha", type="password")
            if st.button("Entrar"):
                users = st.secrets["credentials"]["usernames"]
                if u in users and p == users[u]:
                    st.session_state["password_correct"] = True
                    st.session_state["user_logado"] = u
                    st.rerun()
                else: st.error("Erro de acesso.")

if __name__ == "__main__":
    main()
