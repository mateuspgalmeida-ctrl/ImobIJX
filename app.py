import streamlit as st
import pandas as pd
import numpy as np
import os
import gspread
import plotly.express as px
import plotly.graph_objects as go
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import io

# --- 1. CONFIGURAÇÃO DE PÁGINA ---
st.set_page_config(page_title="ImobIJX | Master Intelligence ERP", layout="wide", page_icon="🏢")

# --- 2. CONFIGURAÇÕES DE NEGÓCIO ---
STATUS_CLIENTE = ["Lead", "Cliente Potencial", "Cliente Realizado", "Cliente Fidelizado"]
BAIRROS_FEIRA = ["SIM", "Santa Mônica", "Papagaio", "Noide Cerqueira", "Kalilândia", "Centro", "Muchila", "Tomba", "Outros"]
DIAS_LIMITE_PARADO = 10

# --- 3. ESTILO CSS CUSTOMIZADO ---
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; font-family: 'Inter', sans-serif; }
    .kpi-card {
        background: white; padding: 25px; border-radius: 15px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        border-top: 5px solid #007a7c; text-align: center;
    }
    .mural-master {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        color: #fbbf24; padding: 30px; border-radius: 20px;
        border-left: 10px solid #fbbf24; margin-bottom: 30px;
    }
    .master-badge { background-color: #1e293b; color: #fbbf24; padding: 5px 15px; border-radius: 8px; font-size: 12px; font-weight: 800; border: 1px solid #fbbf24; }
    .admin-badge { background-color: #007a7c; color: white; padding: 5px 15px; border-radius: 8px; font-size: 12px; font-weight: 600; }
    .alerta-box { background-color: #fff1f2; border-left: 5px solid #e11d48; padding: 20px; border-radius: 10px; color: #9f1239; font-weight: 700; margin-bottom: 20px; }
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

def identificar_leads_parados(df):
    if df.empty: return pd.DataFrame()
    limite = datetime.now() - timedelta(days=DIAS_LIMITE_PARADO)
    return df[(df['Status'].isin(['Lead', 'Cliente Potencial'])) & (df['Data'] <= limite)]

# --- 5. MAIN APP ---
def main():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    with st.sidebar:
        if os.path.exists("logo.jpg"): st.image("logo.jpg", use_container_width=True)
        else: st.markdown("<h1 style='text-align:center; color:#007a7c;'>🏢 ImobIJX</h1>", unsafe_allow_html=True)
        
        st.divider()
        if st.session_state["password_correct"]:
            user_logado = st.session_state.get('user_logado', '').lower()
            if user_logado == "mateus":
                st.markdown(f"👑 **{user_logado.upper()}** <br><span class='master-badge'>MASTER ACCESS</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"👤 **{user_logado.upper()}** <br><span class='admin-badge'>ADMINISTRATIVO</span>", unsafe_allow_html=True)
            
            menu = st.radio("SISTEMA GESTÃO", [
                "🏛️ Mural Master", "📊 Dashboard Geral", "🔥 Zonas de Calor",
                "🤝 CRM Clientes", "🏆 Ranking Performance", "🧠 People Analytics", 
                "👥 Equipe", "💰 Vendas", "📄 Banco de Talentos"
            ])
            
            if st.button("🚪 Sair"):
                st.session_state["password_correct"] = False
                st.rerun()
        else:
            menu = st.radio("NAVEGAÇÃO", ["🏠 Início", "🔐 Painel Restrito"])

    # --- 6. LOGICA DE TELAS ---
    if st.session_state["password_correct"]:
        df_corr = buscar_dados(0)
        df_vendas = buscar_dados(1)
        df_cv = buscar_dados(2)
        df_clientes = buscar_dados(3)

        if menu == "🏛️ Mural Master":
            st.title("🏛️ Mural de Avisos Master")
            st.markdown("""<div class="mural-master"><h3>📢 Alinhamento Estratégico 2026</h3><p>Foco no SIM e Noide Cerqueira. Limpem os leads parados!</p></div>""", unsafe_allow_html=True)

        elif menu == "📊 Dashboard Geral":
            st.title("📊 Dashboard")
            leads_parados = identificar_leads_parados(df_clientes)
            if not leads_parados.empty:
                st.markdown(f'<div class="alerta-box">⚠️ {len(leads_parados)} leads parados há mais de 10 dias!</div>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f'<div class="kpi-card"><p class="kpi-label">CRM</p><p class="kpi-val">{len(df_clientes)}</p></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="kpi-card"><p class="kpi-label">Vendas</p><p class="kpi-val">{len(df_vendas)}</p></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="kpi-card"><p class="kpi-label">Leads Novos</p><p class="kpi-val">{len(df_clientes[df_clientes["Status"]=="Lead"])}</p></div>', unsafe_allow_html=True)

        elif menu == "🔥 Zonas de Calor":
            st.title("🔥 Zonas de Calor")
            if not df_clientes.empty and 'Bairro' in df_clientes.columns:
                heat = df_clientes['Bairro'].value_counts().reset_index()
                heat.columns = ['Bairro', 'Volume']
                st.plotly_chart(px.bar(heat, x='Bairro', y='Volume', color='Volume', color_continuous_scale='OrRd'))

        elif menu == "🤝 CRM Clientes":
            st.title("🤝 CRM")
            tab1, tab2 = st.tabs(["Base", "Novo"])
            with tab1: st.dataframe(df_clientes, use_container_width=True)
            with tab2:
                with st.form("add"):
                    n = st.text_input("Nome")
                    b = st.selectbox("Bairro", BAIRROS_FEIRA)
                    s = st.selectbox("Status", STATUS_CLIENTE)
                    if st.form_submit_button("Salvar"):
                        gc = conecta_planilha()
                        gc.get_worksheet(3).append_row([datetime.now().strftime('%d/%m/%Y'), n, "", s, b, "Portal", "Gestão"])
                        st.success("Salvo!")
                        st.cache_data.clear()

        elif menu == "🏆 Ranking Performance":
            st.title("🏆 Ranking")
            if not df_clientes.empty:
                # Corrigido o erro de sintaxe aqui
                parados_ranking = identificar_leads_parados(df_clientes).groupby('Corretor').size().reset_index(name='Leads Parados')
                st.subheader("Leads Esquecidos por Corretor")
                st.dataframe(parados_ranking, use_container_width=True)
                st.plotly_chart(px.pie(df_clientes, names='Corretor', title="Distribuição Geral"))

        elif menu == "🧠 People Analytics":
            st.title("🧠 People Analytics")
            fig = go.Figure(data=go.Scatterpolar(r=[4, 5, 4, 3, 5], theta=['Vendas','Processos','Foco','Clima','Engajamento'], fill='toself'))
            st.plotly_chart(fig)

        elif menu == "👥 Equipe":
            st.dataframe(df_corr, use_container_width=True)
        elif menu == "💰 Vendas":
            st.dataframe(df_vendas, use_container_width=True)
        elif menu == "📄 Banco de Talentos":
            st.dataframe(df_cv, use_container_width=True)

    else:
        if menu == "🏠 Início":
            st.markdown("<h1 style='text-align:center;'>Imobiliária Janeide Xavier</h1>", unsafe_allow_html=True)
        elif menu == "🔐 Painel Restrito":
            u = st.text_input("Usuário").lower().strip()
            p = st.text_input("Senha", type="password")
            if st.button("Entrar"):
                users = st.secrets["credentials"]["usernames"]
                if u in users and p == users[u]:
                    st.session_state["password_correct"] = True
                    st.session_state["user_logado"] = u
                    st.rerun()
                else: st.error("Erro!")

    st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 11px; margin-top:50px;'>© 2026 ImobIJX</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
