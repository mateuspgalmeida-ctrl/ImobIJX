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

# --- 2. FUNÇÃO SEGURA PARA ANIMAÇÃO (LOTTIE) ---
def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200: return None
        return r.json()
    except: return None

# URL de animação imobiliária estável
lottie_url = "https://lottie.host/573612d1-2905-4927-9976-f3689c177b96/K2p27X9Rz8.json"
lottie_anim = load_lottieurl(lottie_url)

# --- 3. ESTILO CSS PARA PERSONALIZAR A ÁREA CENTRAL ---
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    [data-testid="stSidebar"] { background-color: #1e293b; color: white; }
    .main-title { color: #007a7c; text-align: center; font-weight: 800; font-size: 3rem; margin-bottom: 0px; }
    .sub-title { color: #64748b; text-align: center; font-size: 1.2rem; margin-bottom: 40px; }
    .kpi-card {
        background: white; padding: 25px; border-radius: 15px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        border-top: 5px solid #007a7c; text-align: center; color: #1e293b;
    }
    .mural-master {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        color: #fbbf24; padding: 30px; border-radius: 20px;
        border-left: 10px solid #fbbf24; margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. FUNÇÕES DE DADOS ---
@st.cache_resource
def conecta_planilha():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        return gspread.authorize(creds).open("Dados_ImobIJX")
    except: return None

@st.cache_data(ttl=300)
def buscar_dados(aba_index):
    gc = conecta_planilha()
    if gc:
        try:
            df = pd.DataFrame(gc.get_worksheet(aba_index).get_all_records())
            if 'Data' in df.columns:
                df['Data'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce')
            return df
        except: return pd.DataFrame()
    return pd.DataFrame()

# --- 5. LÓGICA DO APP ---
def main():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    # SIDEBAR
    with st.sidebar:
        col1, col2, col3 = st.columns([1, 5, 1])
        with col2:
            if os.path.exists("logo.jpg"): st.image("logo.jpg", use_container_width=True)
            else: st.markdown("<h2 style='text-align:center;'>🏢 ImobIJX</h2>", unsafe_allow_html=True)
        
        st.divider()
        if st.session_state["password_correct"]:
            user = st.session_state.get('user_logado', '').upper()
            st.markdown(f"👤 **{user}**")
            menu = st.radio("SISTEMA GESTÃO", ["🏛️ Início & Mural", "📊 Dashboard", "🔥 Zonas de Calor", "🤝 CRM", "📄 Talentos"])
            if st.button("🚪 Sair"):
                st.session_state["password_correct"] = False
                st.rerun()
        else:
            menu = st.radio("NAVEGAÇÃO", ["🏠 Início", "🎯 Trabalhe Conosco", "🔐 Painel Restrito"])

    # CONTEÚDO CENTRAL
    if st.session_state["password_correct"]:
        df_clientes = buscar_dados(3)
        df_vendas = buscar_dados(1)
        df_cv = buscar_dados(2)

        if menu == "🏛️ Início & Mural":
            st.markdown("<h1 class='main-title'>Imobiliária Janeide Xavier LTDA</h1>", unsafe_allow_html=True)
            st.markdown("<p class='sub-title'>Inteligência e Gestão de Alta Performance</p>", unsafe_allow_html=True)
            
            st.markdown(f"""
                <div class="mural-master">
                    <h3>📢 Mural Master - Bem-vindo, {st.session_state['user_logado'].capitalize()}</h3>
                    <p>Foco Estratégico: <b>SIM e Noide Cerqueira</b>. Priorize o atendimento dos leads parados.</p>
                </div>
            """, unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f'<div class="kpi-card"><p>Base CRM</p><h3>{len(df_clientes)}</h3></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="kpi-card"><p>Vendas</p><h3>{len(df_vendas)}</h3></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="kpi-card"><p>Currículos</p><h3>{len(df_cv)}</h3></div>', unsafe_allow_html=True)

        elif menu == "📊 Dashboard":
            st.title("📊 Indicadores")
            if not df_clientes.empty:
                fig = px.pie(df_clientes, names='Status', hole=0.4, title="Status dos Clientes")
                st.plotly_chart(fig, use_container_width=True)

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
            st.markdown("<h1 class='main-title'>Imobiliária Janeide Xavier LTDA</h1>", unsafe_allow_html=True)
            st.markdown("<p class='sub-title'>Inovação no Mercado Imobiliário de Feira de Santana</p>", unsafe_allow_html=True)
            
            # Animação Central Segura
            if lottie_anim:
                st_lottie(lottie_anim, height=350, key="home_anim")
            
        elif menu == "🎯 Trabalhe Conosco":
            st.markdown("<h1 style='color:#007a7c;'>🎯 Faça Parte do Time</h1>", unsafe_allow_html=True)
            st.write("Envie seus dados e currículo para análise da nossa equipe.")
            with st.form("cv_recrutamento"):
                nome = st.text_input("Nome Completo")
                zap = st.text_input("WhatsApp (com DDD)")
                link = st.text_input("Link do Currículo (Drive ou LinkedIn)")
                if st.form_submit_button("Enviar Candidatura"):
                    gc = conecta_planilha()
                    if gc:
                        gc.get_worksheet(2).append_row([datetime.now().strftime('%d/%m/%Y'), nome, zap, "Candidato", link])
                        st.success("Candidatura enviada com sucesso!")
                    else: st.error("Erro ao conectar com o banco de dados.")

        elif menu == "🔐 Painel Restrito":
            st.subheader("Login Administrativo")
            u = st.text_input("Usuário").lower().strip()
            p = st.text_input("Senha", type="password")
            if st.button("Acessar"):
                users = st.secrets["credentials"]["usernames"]
                if u in users and p == users[u]:
                    st.session_state["password_correct"] = True
                    st.session_state["user_logado"] = u
                    st.rerun()
                else: st.error("Dados inválidos.")

    st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 11px; margin-top:100px;'>© 2026 Imobiliária Janeide Xavier LTDA</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
