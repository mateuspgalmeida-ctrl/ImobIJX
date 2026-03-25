import streamlit as st
import pandas as pd
import numpy as np
import os
import gspread
import plotly.express as px
import plotly.graph_objects as go
from google.oauth2.service_account import Credentials
from datetime import datetime
import re

# --- CONFIGURAÇÃO DE PÁGINA ---
st.set_page_config(page_title="ImobIJX | Master Intelligence", layout="wide", page_icon="🏢")

# --- CONFIGURAÇÕES DE NEGÓCIO ---
STATUS_CLIENTE = ["Lead", "Cliente Potencial", "Cliente Realizado", "Cliente Fidelizado"]
MESES_PT = {1:'Jan', 2:'Fev', 3:'Mar', 4:'Abr', 5:'Mai', 6:'Jun', 7:'Jul', 8:'Ago', 9:'Set', 10:'Out', 11:'Nov', 12:'Dez'}

# --- ESTILO CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; font-family: 'Inter', sans-serif; }
    .kpi-card {
        background: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        border-top: 4px solid #007a7c; text-align: center;
    }
    .kpi-label { color: #64748b; font-size: 0.85rem; font-weight: 600; text-transform: uppercase; }
    .kpi-val { color: #0f172a; font-size: 1.8rem; font-weight: 800; }
    .master-badge { background-color: #1e293b; color: #fbbf24; padding: 4px 12px; border-radius: 6px; font-size: 11px; font-weight: 800; border: 1px solid #fbbf24; }
    .admin-badge { background-color: #007a7c; color: white; padding: 4px 12px; border-radius: 6px; font-size: 11px; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE CONEXÃO ---
@st.cache_resource
def conecta_planilha():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(creds)
        return client.open("Dados_ImobIJX")
    except: return None

@st.cache_data(ttl=300)
def buscar_dados(aba_index):
    gc = conecta_planilha()
    if gc:
        try:
            return pd.DataFrame(gc.get_worksheet(aba_index).get_all_records())
        except: return pd.DataFrame()
    return pd.DataFrame()

# --- MAIN APP ---
def main():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    # --- SIDEBAR ---
    with st.sidebar:
        if os.path.exists("logo.jpg"): st.image("logo.jpg", use_container_width=True)
        else: st.markdown("<h2 style='text-align:center; color:#007a7c;'>🏢 ImobIJX</h2>", unsafe_allow_html=True)
        
        st.divider()
        if not st.session_state["password_correct"]:
            menu = st.radio("NAVEGAÇÃO", ["🏠 Início", "🎯 Trabalhe Conosco", "🔐 Painel Restrito"])
        else:
            user_logado = st.session_state.get('user_logado', '').lower()
            
            # --- DIFERENCIAÇÃO DE NÍVEL ---
            if user_logado == "mateus":
                st.markdown(f"👑 **{user_logado.upper()}** <br><span class='master-badge'>MASTER ACCESS</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"👤 **{user_logado.upper()}** <br><span class='admin-badge'>ADMINISTRATIVO</span>", unsafe_allow_html=True)
            
            st.write("")
            # Acesso total para os três usuários
            menu = st.radio("SISTEMA GESTÃO", ["📊 Dashboard", "🤝 CRM Clientes", "🧠 People Analytics", "👥 Corretores", "💰 Vendas", "📄 Currículos"])
            
            st.divider()
            if st.button("🚪 Sair"):
                st.session_state["password_correct"] = False
                st.rerun()

    # --- CARGA DE DADOS ---
    df_corr = buscar_dados(0)
    df_vendas = buscar_dados(1)
    df_cv = buscar_dados(2)
    df_clientes = buscar_dados(3)

    # --- TELAS ADMINISTRATIVAS ---
    if st.session_state["password_correct"]:
        
        if menu == "📊 Dashboard":
            st.title(f"📊 Dashboard Geral")
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f'<div class="kpi-card"><p class="kpi-label">Base CRM</p><p class="kpi-val">{len(df_clientes)}</p></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="kpi-card"><p class="kpi-label">Leads Novos</p><p class="kpi-val">{len(df_clientes[df_clientes["Status"]=="Lead"]) if not df_clientes.empty else 0}</p></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="kpi-card"><p class="kpi-label">VGV Registrados</p><p class="kpi-val">{len(df_vendas)}</p></div>', unsafe_allow_html=True)
            
            if not df_clientes.empty:
                funil_data = df_clientes['Status'].value_counts().reindex(STATUS_CLIENTE).fillna(0)
                st.plotly_chart(px.funnel(x=funil_data.values, y=funil_data.index, title="Funil de Conversão ImobIJX", color_discrete_sequence=['#007a7c']), use_container_width=True)

        elif menu == "🤝 CRM Clientes":
            st.title("🤝 Gestão de Relacionamento")
            tab_base, tab_novo = st.tabs(["📋 Todos os Clientes", "➕ Adicionar Lead"])
            with tab_base: st.dataframe(df_clientes, use_container_width=True)
            with tab_novo:
                with st.form("form_crm"):
                    n = st.text_input("Nome do Cliente")
                    t = st.text_input("WhatsApp")
                    s = st.selectbox("Classificação", STATUS_CLIENTE)
                    corr = st.selectbox("Corretor", df_corr['Nome'].unique() if not df_corr.empty else ["Gestão"])
                    if st.form_submit_button("Cadastrar Cliente"):
                        gc = conecta_planilha()
                        gc.get_worksheet(3).append_row([datetime.now().strftime('%d/%m/%Y'), n, t, s, "", "Portal Interno", corr])
                        st.success(f"Registrado com sucesso por {st.session_state['user_logado']}")
                        st.cache_data.clear()
                        st.rerun()

        elif menu == "🧠 People Analytics":
            st.title("🧠 People Analytics & Talentos")
            st.write("Análise comportamental e indicadores de RH.")
            # Radar de competências médio da equipe
            fig = go.Figure(data=go.Scatterpolar(r=[4, 5, 4, 3, 4], theta=['Vendas','Processos','Foco','Clima','Engajamento'], fill='toself'))
            st.plotly_chart(fig)

        elif menu == "👥 Corretores":
            st.title("👥 Gestão de Equipe")
            st.dataframe(df_corr, use_container_width=True)

        elif menu == "💰 Vendas":
            st.title("💰 Histórico de Vendas")
            st.dataframe(df_vendas, use_container_width=True)

        elif menu == "📄 Currículos":
            st.title("📄 Banco de Talentos")
            st.dataframe(df_cv, use_container_width=True)

    # --- TELAS PÚBLICAS ---
    else: 
        if menu == "🏠 Início":
            st.markdown("<h1 style='text-align: center; color: #007a7c; padding-top: 50px;'>Imobiliária Janeide Xavier LTDA</h1>", unsafe_allow_html=True)
            st.info("Utilize o menu lateral para acesso restrito.")
            
        elif menu == "🎯 Trabalhe Conosco":
            st.title("🎯 Faça parte do nosso time")
            with st.form("cv_public"):
                n_cv = st.text_input("Nome Completo")
                t_cv = st.text_input("WhatsApp")
                if st.form_submit_button("Enviar Currículo"):
                    gc = conecta_planilha()
                    gc.get_worksheet(2).append_row([datetime.now().strftime('%d/%m/%Y'), n_cv, t_cv, "Via Portal", "Candidato"])
                    st.success("Recebido com sucesso!")

        elif menu == "🔐 Painel Restrito":
            st.subheader("Login Administrativo")
            u = st.text_input("Usuário").lower().strip()
            p = st.text_input("Senha", type="password")
            if st.button("Entrar no Sistema", type="primary"):
                try:
                    credentials = st.secrets["credentials"]["usernames"]
                    if u in credentials and p == credentials[u]:
                        st.session_state["password_correct"] = True
                        st.session_state["user_logado"] = u
                        st.rerun()
                    else: st.error("Usuário ou senha inválidos.")
                except: st.error("Erro técnico nos Secrets do Streamlit.")

    st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 11px; margin-top:50px;'>© 2026 ImobIJX | Master Intelligence Collaboration</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
