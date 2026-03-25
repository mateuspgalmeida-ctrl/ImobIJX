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

# --- CONFIGURAÇÃO DE PÁGINA ---
st.set_page_config(page_title="ImobIJX | Master Intelligence ERP", layout="wide", page_icon="🏢")

# --- CONFIGURAÇÕES DE NEGÓCIO ---
STATUS_CLIENTE = ["Lead", "Cliente Potencial", "Cliente Realizado", "Cliente Fidelizado"]
BAIRROS_FEIRA = ["SIM", "Santa Mônica", "Papagaio", "Noide Cerqueira", "Kalilândia", "Centro", "Muchila", "Tomba", "Outros"]
DIAS_LIMITE_PARADO = 10

# --- ESTILO CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; font-family: 'Inter', sans-serif; }
    .kpi-card {
        background: white; padding: 20px; border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        border-top: 4px solid #007a7c; text-align: center;
    }
    .mural-master {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        color: #fbbf24; padding: 25px; border-radius: 15px;
        border-left: 8px solid #fbbf24; margin-bottom: 25px;
    }
    .master-badge { background-color: #1e293b; color: #fbbf24; padding: 4px 12px; border-radius: 6px; font-size: 11px; font-weight: 800; border: 1px solid #fbbf24; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE DADOS ---
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

# --- MAIN APP ---
def main():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    with st.sidebar:
        st.markdown("<h2 style='text-align:center; color:#007a7c;'>🏢 ImobIJX</h2>", unsafe_allow_html=True)
        st.divider()
        if st.session_state["password_correct"]:
            user = st.session_state.get('user_logado', '').lower()
            badge = "MASTER" if user == "mateus" else "ADMIN"
            st.markdown(f"👤 **{user.upper()}** <span class='master-badge'>{badge}</span>", unsafe_allow_html=True)
            menu = st.radio("SISTEMA", ["🏛️ Mural Master", "🔥 Zonas de Calor", "📊 Dashboard", "🤝 CRM & Bairros", "🏆 Ranking Performance", "🧠 People Analytics", "📄 Recrutamento Tech"])
            if st.button("🚪 Sair"):
                st.session_state["password_correct"] = False
                st.rerun()
        else:
            menu = st.radio("NAVEGAÇÃO", ["🏠 Início", "🔐 Painel Restrito"])

    if st.session_state["password_correct"]:
        df_corr = buscar_dados(0)
        df_vendas = buscar_dados(1)
        df_cv = buscar_dados(2)
        df_clientes = buscar_dados(3)

        if menu == "🏛️ Mural Master":
            st.title("🏛️ Mural Master")
            st.markdown("""<div class="mural-master"><h3>📢 Alinhamento Estratégico</h3><p>Foco 2026: Dominar o SIM e Noide Cerqueira através de dados.</p></div>""", unsafe_allow_html=True)

        elif menu == "🔥 Zonas de Calor":
            st.title("🔥 Zonas de Calor - Feira de Santana")
            if not df_clientes.empty and 'Bairro' in df_clientes.columns:
                # Mapa de Calor por Volume de Leads
                heat_data = df_clientes['Bairro'].value_counts().reset_index()
                heat_data.columns = ['Bairro', 'Volume']
                
                fig_heat = px.bar(heat_data, x='Bairro', y='Volume', color='Volume', 
                                 title="Volume de Demanda por Bairro",
                                 color_continuous_scale='OrRd', template='plotly_white')
                st.plotly_chart(fig_heat, use_container_width=True)
                
                c1, c2 = st.columns(2)
                with c1:
                    st.metric("Bairro mais Quente", heat_data.iloc[0]['Bairro'] if not heat_data.empty else "N/A")
                with c2:
                    st.metric("Total de Bairros Ativos", len(heat_data))
            else:
                st.warning("Cadastre o 'Bairro' nos seus leads para ver as zonas de calor.")

        elif menu == "📊 Dashboard":
            st.title("📊 Painel Geral")
            # Métricas rápidas
            st.dataframe(df_clientes.tail(5), use_container_width=True)

        elif menu == "🤝 CRM & Bairros":
            st.title("🤝 Gestão de Relacionamento")
            with st.form("add_lead"):
                n = st.text_input("Nome Cliente")
                b = st.selectbox("Bairro", BAIRROS_FEIRA)
                s = st.selectbox("Status", STATUS_CLIENTE)
                if st.form_submit_button("Cadastrar"):
                    gc = conecta_planilha()
                    gc.get_worksheet(3).append_row([datetime.now().strftime('%d/%m/%Y'), n, "", s, b, "Portal", "Gestão"])
                    st.success("Lead salvo!")
                    st.cache_data.clear()

        elif menu == "🏆 Ranking Performance":
            st.title("🏆 Performance da Equipe")
            if not df_clientes.empty:
                ranking = df_clientes['Corretor'].value_counts().reset_index()
                st.plotly_chart(px.pie(ranking, values='count', names='Corretor', title="Distribuição de Leads"))

        elif menu == "📄 Recrutamento Tech":
            st.title("🎯 Recrutamento")
            st.info("Use o argumento de 'Inteligência de Mercado' para atrair corretores de elite.")

    else:
        if menu == "🏠 Início": st.title("Bem-vindo ao Portal ImobIJX")
        elif menu == "🔐 Painel Restrito":
            u = st.text_input("Usuário").lower().strip()
            p = st.text_input("Senha", type="password")
            if st.button("Entrar"):
                creds = st.secrets["credentials"]["usernames"]
                if u in creds and p == creds[u]:
                    st.session_state["password_correct"] = True
                    st.session_state["user_logado"] = u
                    st.rerun()

if __name__ == "__main__":
    main()
