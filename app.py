import streamlit as st
import pandas as pd
import numpy as np
import os
import gspread
import plotly.express as px
import plotly.graph_objects as go
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import requests
from streamlit_lottie import st_lottie

# --- 1. CONFIGURAÇÃO DE PÁGINA ---
st.set_page_config(page_title="ImobIJX | Master Intelligence", layout="wide", page_icon="🏢")

# --- 2. FUNÇÃO SEGURA PARA CARREGAR ANIMAÇÃO ---
def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# URL estável de animação imobiliária (Cidade/Prédios sendo construídos)
lottie_url = "https://lottie.host/573612d1-2905-4927-9976-f3689c177b96/K2p27X9Rz8.json"
lottie_real_estate = load_lottieurl(lottie_url)

# --- 3. CONFIGURAÇÕES DE NEGÓCIO ---
STATUS_CLIENTE = ["Lead", "Cliente Potencial", "Cliente Realizado", "Cliente Fidelizado"]
BAIRROS_FEIRA = ["SIM", "Santa Mônica", "Papagaio", "Noide Cerqueira", "Kalilândia", "Centro", "Muchila", "Tomba", "Outros"]

# --- 4. ESTILO CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #1e293b; color: white; }
    .kpi-card {
        background: white; padding: 25px; border-radius: 15px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        border-top: 5px solid #007a7c; text-align: center; color: #1e293b !important;
    }
    .mural-master {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        color: #fbbf24; padding: 30px; border-radius: 20px;
        border-left: 10px solid #fbbf24; margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 5. FUNÇÕES DE DADOS ---
@st.cache_resource
def conecta_planilha():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        return gspread.authorize(creds).open("Dados_ImobIJX")
    except: return None

@st.cache_data(ttl=300)
def buscar_dados(aba_index):
    # Só mostra a animação se ela foi carregada com sucesso
    if lottie_real_estate:
        with st.spinner("Construindo inteligência..."):
            gc = conecta_planilha()
            if gc:
                df = pd.DataFrame(gc.get_worksheet(aba_index).get_all_records())
                if 'Data' in df.columns:
                    df['Data'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce')
                return df
    return pd.DataFrame()

# --- 6. MAIN APP ---
def main():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    with st.sidebar:
        # Logo Centralizada
        col1, col2, col3 = st.columns([1, 5, 1])
        with col2:
            if os.path.exists("logo.jpg"): st.image("logo.jpg", use_container_width=True)
            else: st.markdown("<h2 style='text-align:center;'>🏢 ImobIJX</h2>", unsafe_allow_html=True)
        
        st.divider()
        if st.session_state["password_correct"]:
            user = st.session_state.get('user_logado', '').upper()
            st.markdown(f"👤 **{user}**")
            menu = st.radio("MENU MASTER", ["🏛️ Início & Mural", "📊 Dashboard", "🔥 Zonas de Calor", "🤝 CRM", "📄 Talentos"])
            if st.button("🚪 Sair"):
                st.session_state["password_correct"] = False
                st.rerun()
        else:
            menu = st.radio("NAVEGAÇÃO", ["🏠 Início", "🎯 Trabalhe Conosco", "🔐 Painel Restrito"])

    # --- 7. TELAS ---
    if st.session_state["password_correct"]:
        df_clientes = buscar_dados(3)
        df_vendas = buscar_dados(1)
        df_cv = buscar_dados(2)

        if menu == "🏛️ Início & Mural":
            st.markdown("<h1 style='color:#007a7c;'>Imobiliária Janeide Xavier LTDA</h1>", unsafe_allow_html=True)
            st.markdown(f"### Bem-vindo, {st.session_state['user_logado'].capitalize()}!")
            
            st.markdown("""<div class="mural-master"><h3>📢 Mural Master</h3><p>Foco: <b>SIM e Noide Cerqueira</b>. Vamos dominar o mercado!</p></div>""", unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f'<div class="kpi-card"><p>Base CRM</p><h3>{len(df_clientes)}</h3></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="kpi-card"><p>Vendas</p><h3>{len(df_vendas)}</h3></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="kpi-card"><p>Currículos</p><h3>{len(df_cv)}</h3></div>', unsafe_allow_html=True)

        elif menu == "📊 Dashboard":
            st.title("📊 Indicadores Gerais")
            if not df_clientes.empty:
                st.plotly_chart(px.pie(df_clientes, names='Status', title="Distribuição de Status", color_discrete_sequence=px.colors.qualitative.Prism))

        elif menu == "🔥 Zonas de Calor":
            st.title("🔥 Zonas de Calor - Feira de Santana")
            if not df_clientes.empty:
                heat = df_clientes['Bairro'].value_counts().reset_index()
                st.plotly_chart(px.bar(heat, x='Bairro', y='count', color='count', color_continuous_scale='OrRd'))

        elif menu == "🤝 CRM":
            st.title("🤝 Gestão CRM")
            st.dataframe(df_clientes, use_container_width=True)

        elif menu == "📄 Talentos":
            st.title("📄 Banco de Talentos")
            st.dataframe(df_cv, use_container_width=True)

    else:
        if menu == "🏠 Início":
            st.markdown("<h1 style='text-align:center; color:#007a7c; margin-top:50px;'>Imobiliária Janeide Xavier LTDA</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align:center;'>Inteligência e Gestão Imobiliária Master</p>", unsafe_allow_html=True)
            # Animação segura na Home
            if lottie_real_estate:
                st_lottie(lottie_real_estate, height=400, key="home_anim")
            
        elif menu == "🎯 Trabalhe Conosco":
            st.title("🎯 Trabalhe Conosco")
            with st.form("cv_publico"):
                nome = st.text_input("Nome")
                zap = st.text_input("WhatsApp")
                link = st.text_input("Link Currículo/LinkedIn")
                if st.form_submit_button("Enviar"):
                    gc = conecta_planilha()
                    gc.get_worksheet(2).append_row([datetime.now().strftime('%d/%m/%Y'), nome, zap, "Interessado", link])
                    st.success("Recebemos seus dados!")

        elif menu == "🔐 Painel Restrito":
            st.subheader("Acesso Administrativo")
            u = st.text_input("Usuário").lower().strip()
            p = st.text_input("Senha", type="password")
            if st.button("Logar"):
                users = st.secrets["credentials"]["usernames"]
                if u in users and p == users[u]:
                    st.session_state["password_correct"] = True
                    st.session_state["user_logado"] = u
                    st.rerun()
                else: st.error("Usuário ou senha inválidos.")

    st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 11px; margin-top:100px;'>© 2026 ImobIJX</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
