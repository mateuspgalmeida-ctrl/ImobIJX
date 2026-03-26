import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import requests
from streamlit_lottie import st_lottie
import os
import plotly.express as px

# --- 1. CONFIGURAÇÃO DE PÁGINA ---
st.set_page_config(page_title="ImobIJX | Master Intelligence", layout="wide", page_icon="🏢")

# --- 2. FUNÇÃO ANIMAÇÃO ---
def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else None
    except: return None

lottie_anim = load_lottieurl("https://lottie.host/573612d1-2905-4927-9976-f3689c177b96/K2p27X9Rz8.json")

# --- 3. CSS GLOBAL (ESTILO PRESERVADO) ---
st.markdown("""
    <style>
    .stApp { background-color: #f1f5f9; }
    h1, h2, h3, p, span, label { color: #007a7c !important; font-family: 'Inter', sans-serif; }
    
    .moldura-3d {
        background: #f1f5f9; padding: 40px; border-radius: 30px;
        box-shadow: 20px 20px 60px #d1d5db, -20px -20px 60px #ffffff;
        text-align: center; margin-bottom: 30px;
    }
    
    /* Texto branco ao digitar */
    input { color: white !important; -webkit-text-fill-color: white !important; }
    
    /* Botões Master */
    .stButton>button { 
        background-color: #007a7c !important; color: white !important; 
        border-radius: 10px; font-weight: bold !important; width: 100%;
    }
    .stButton>button p { color: white !important; }
    
    /* Mural Master */
    .mural-master {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        color: #fbbf24 !important; padding: 25px; border-radius: 20px;
        border-left: 10px solid #fbbf24; margin: 25px 0;
    }
    .mural-master h3, .mural-master p { color: #fbbf24 !important; }
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

# --- 5. LOGICA PRINCIPAL ---
def main():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    with st.sidebar:
        if os.path.exists("logo.jpg"): st.image("logo.jpg", use_container_width=True)
        st.divider()
        if st.session_state["password_correct"]:
            st.markdown(f"👤 **{st.session_state.get('user_logado', 'Master').upper()}**")
            # RESTAURADO: Menu Completo
            menu = st.radio("SISTEMA MASTER", [
                "🏛️ Dashboard", 
                "🔥 Zonas de Calor", 
                "🤝 CRM Clientes", 
                "📄 Banco Talentos",
                "📊 Metas e VGV"
            ])
            if st.button("🚪 Sair"):
                st.session_state["password_correct"] = False
                st.rerun()
        else:
            menu = st.radio("MENU PÚBLICO", ["🏠 Início", "🎯 Trabalhe Conosco", "🔐 Acesso Master"])

    # --- CONTEÚDO ---
    if st.session_state["password_correct"]:
        st.markdown('<div class="moldura-3d"><h1>Janeide Xavier LTDA</h1><p>Painel Master de Inteligência</p></div>', unsafe_allow_html=True)
        
        df_clientes = buscar_dados(3) # Aba do CRM

        if menu == "🏛️ Dashboard":
            st.markdown("""<div class="mural-master"><h3>📢 Mural Master</h3><p>Foco total no <b>SIM e Noide Cerqueira</b>! Verifique os leads pendentes.</p></div>""", unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("Leads Totais", len(df_clientes))
            with c2: st.metric("Status", "Operacional")
            with c3: st.metric("Foco", "VGV Feira")
            
        elif menu == "🔥 Zonas de Calor":
            st.title("🔥 Zonas de Calor - Bairros")
            if not df_clientes.empty and 'Bairro' in df_clientes.columns:
                fig = px.bar(df_clientes['Bairro'].value_counts().reset_index(), x='Bairro', y='count', color='count', color_continuous_scale='Reds')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Aguardando dados de bairros para gerar o mapa de calor.")

        elif menu == "🤝 CRM Clientes":
            st.title("🤝 Gestão de Clientes")
            st.dataframe(df_clientes, use_container_width=True)

        elif menu == "📄 Banco Talentos":
            st.title("📄 Currículos Recebidos")
            df_talentos = buscar_dados(2)
            st.dataframe(df_talentos, use_container_width=True)
            
        elif menu == "📊 Metas e VGV":
            st.title("📊 Gestão de Metas")
            st.write("Módulo em desenvolvimento para cálculo de VGV automático.")

    else:
        # TELAS PÚBLICAS
        if menu == "🏠 Início":
            st.markdown(f'''<div class="moldura-3d"><h1>Janeide Xavier LTDA</h1>
                <p style="font-size: 1.5rem; font-weight: 500;">Onde a tradição de Feira de Santana encontra a inteligência de dados.</p></div>''', unsafe_allow_html=True)
            if lottie_anim: st_lottie(lottie_anim, height=350)
            
        elif menu == "🎯 Trabalhe Conosco":
            st.markdown('<div class="moldura-3d"><h1>Trabalhe Conosco</h1></div>', unsafe_allow_html=True)
            with st.form("cv_form"):
                n = st.text_input("Nome Completo")
                z = st.text_input("WhatsApp")
                l = st.text_input("Link do Currículo")
                if st.form_submit_button("Enviar Candidatura"):
                    gc = conecta_planilha()
                    if gc:
                        gc.get_worksheet(2).append_row([datetime.now().strftime('%d/%m/%Y'), n, z, "Candidato", l])
                        st.success("Sucesso! Aguarde nosso contato.")

        elif menu == "🔐 Acesso Master":
            st.markdown('<div class="moldura-3d"><h1>Login Master</h1></div>', unsafe_allow_html=True)
            u = st.text_input("Usuário").lower().strip()
            p = st.text_input("Senha", type="password")
            if st.button("Acessar Painel"):
                if u in st.secrets["credentials"]["usernames"] and p == st.secrets["credentials"]["usernames"][u]:
                    st.session_state["password_correct"] = True
                    st.session_state["user_logado"] = u
                    st.rerun()
                else: st.error("Usuário ou senha inválidos.")

    st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 11px; margin-top:100px;'>© 2026 Imobiliária Janeide Xavier LTDA</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
