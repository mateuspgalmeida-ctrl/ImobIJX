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

# --- 3. CSS PARA MOLDURA 3D E ESTILO PREMIUM ---
st.markdown("""
    <style>
    .stApp { background-color: #f1f5f9; }
    
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

    .mural-master {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        color: #fbbf24; padding: 25px; border-radius: 20px;
        border-left: 10px solid #fbbf24; margin: 25px 0;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
    }
    
    .kpi-card {
        background: white; padding: 25px; border-radius: 20px;
        box-shadow: 10px 10px 30px #d1d5db;
        text-align: center; border-bottom: 5px solid #007a7c;
        color: #1e293b;
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
        # Tenta carregar a logo na lateral
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
        df_clientes = buscar_dados(3)
        
        if menu == "🏛️ Dashboard":
            # Moldura 3D com o Nome da Empresa
            st.markdown(f'''
                <div class="moldura-3d">
                    <h1 class="titulo-principal">Janeide Xavier LTDA</h1>
                    <p class="subtitulo-principal">Painel Master de Inteligência Imobiliária</p>
                </div>
            ''', unsafe_allow_html=True)
            
            st.markdown("""<div class="mural-master"><h3>📢 Mural Estratégico</h3><p>Foco na <b>Noide Cerqueira e SIM</b>. Verifique o funil de vendas hoje!</p></div>""", unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f'<div class="kpi-card"><h5>Volume CRM</h5><h2>{len(df_clientes)}</h2></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="kpi-card"><h5>Vendas</h5><h2>Ativas</h2></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="kpi-card"><h5>Status</h5><h2>Operacional</h2></div>', unsafe_allow_html=True)

        elif menu == "🔥 Zonas de Calor":
            st.title("🔥 Zonas de Calor - Feira de Santana")
            if not df_clientes.empty:
                st.plotly_chart(px.bar(df_clientes['Bairro'].value_counts().reset_index(), x='Bairro', y='count', color='count', color_continuous_scale='Reds'))

        elif menu == "🤝 CRM Clientes":
            st.title("🤝 Gestão de Clientes")
            st.dataframe(df_clientes, use_container_width=True)

        elif menu == "📄 Banco Talentos":
            st.title("📄 Currículos Recebidos")
            st.dataframe(buscar_dados(2), use_container_width=True)

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
                    n = st.text_input("Nome Completo")
                    w = st.text_input("WhatsApp (com DDD)")
                    l = st.text_input("Link do LinkedIn ou Currículo")
                    if st.form_submit_button("Enviar Candidatura"):
                        gc = conecta_planilha()
                        if gc:
                            gc.get_worksheet(2).append_row([datetime.now().strftime('%d/%m/%Y'), n, w, "Candidato", l])
                            st.success("Candidatura enviada com sucesso!")

        elif menu == "🔐 Acesso Master":
            st.markdown('<div class="moldura-3d"><h1 class="titulo-principal">Login Master</h1></div>', unsafe_allow_html=True)
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
