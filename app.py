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
st.set_page_config(page_title="ImobIJX | Gestão Inteligente", layout="wide", page_icon="🏢")

# --- CONFIGURAÇÕES DE NEGÓCIO ---
META_MENSAL_LOJA = 50000.00
STATUS_CLIENTE = ["Lead", "Cliente Potencial", "Cliente Realizado", "Cliente Fidelizado"]
TAXAS_COMISSAO = {
    "Venda (Imóvel Novo/Planta)": 0.05,
    "Venda (Usado/Terceiros)": 0.06,
    "Aluguel (1º Aluguel Integral)": 1.00,
    "Administração Mensal": 0.10,
    "Consultoria/Avaliação": 0.20
}

MESES_PT = {1:'Jan', 2:'Fev', 3:'Mar', 4:'Abr', 5:'Mai', 6:'Jun', 
            7:'Jul', 8:'Ago', 9:'Set', 10:'Out', 11:'Nov', 12:'Dez'}

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
    .sidebar-user { font-weight: 700; color: #007a7c; font-size: 1.1rem; }
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

@st.cache_data(ttl=600)
def buscar_dados(aba_index):
    gc = conecta_planilha()
    if gc:
        try:
            data = gc.get_worksheet(aba_index).get_all_records()
            return pd.DataFrame(data)
        except: return pd.DataFrame()
    return pd.DataFrame()

def limpar_moeda(valor):
    if isinstance(valor, str):
        valor = re.sub(r'[R\$\.\s]', '', valor).replace(',', '.')
    try: return float(valor)
    except: return 0.0

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
            # Identificação do usuário logado (Janeide ou Gessica)
            u_name = st.session_state.get('user_logado', 'Usuário').capitalize()
            st.markdown(f"Bem-vinda, <span class='sidebar-user'>{u_name}</span>!", unsafe_allow_html=True)
            
            # Ambas têm acesso a TODAS as opções abaixo
            menu = st.radio("ADMINISTRAÇÃO", [
                "📊 Dashboard", 
                "🤝 Clientes (CRM)", 
                "🧠 People Analytics", 
                "👥 Corretores", 
                "💰 Vendas", 
                "📄 Currículos"
            ])
            
            st.divider()
            hoje = datetime.now()
            ano_sel = st.selectbox("Ano", [hoje.year, hoje.year-1], index=0)
            mes_sel_nome = st.selectbox("Mês", list(MESES_PT.values()), index=hoje.month-1)
            mes_sel_num = [k for k, v in MESES_PT.items() if v == mes_sel_nome][0]
            
            if st.button("🚪 Sair do Sistema"):
                st.session_state["password_correct"] = False
                st.rerun()

    # --- CARGA DE DADOS ---
    df_corr = buscar_dados(0)
    df_vendas_raw = buscar_dados(1)
    df_cv = buscar_dados(2)
    df_clientes = buscar_dados(3)

    # --- TELAS ADMINISTRATIVAS (ACESSO TOTAL) ---
    if st.session_state["password_correct"]:
        
        if menu == "📊 Dashboard":
            st.title(f"📊 Painel de Controle - {mes_sel_nome}/{ano_sel}")
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f'<div class="kpi-card"><p class="kpi-label">Total Clientes</p><p class="kpi-val">{len(df_clientes)}</p></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="kpi-card"><p class="kpi-label">Leads Ativos</p><p class="kpi-val">{len(df_clientes[df_clientes["Status"]=="Lead"]) if not df_clientes.empty else 0}</p></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="kpi-card"><p class="kpi-label">Time de Vendas</p><p class="kpi-val">{len(df_corr)}</p></div>', unsafe_allow_html=True)
            
            if not df_clientes.empty:
                funil_data = df_clientes['Status'].value_counts().reindex(STATUS_CLIENTE).fillna(0)
                fig_funil = px.funnel(x=funil_data.values, y=funil_data.index, title="Funil Estratégico", color_discrete_sequence=['#007a7c'])
                st.plotly_chart(fig_funil, use_container_width=True)

        elif menu == "🤝 Clientes (CRM)":
            st.title("🤝 Gestão de Relacionamento (CRM)")
            tab_ver, tab_add = st.tabs(["🔍 Visualizar Base", "📝 Novo Cadastro"])
            with tab_ver:
                st.dataframe(df_clientes, use_container_width=True)
            with tab_add:
                with st.form("crm_form"):
                    nome = st.text_input("Nome do Cliente")
                    fone = st.text_input("WhatsApp")
                    stt = st.selectbox("Status Atual", STATUS_CLIENTE)
                    corr = st.selectbox("Corretor Responsável", df_corr['Nome'].unique() if not df_corr.empty else ["Gestão"])
                    if st.form_submit_button("Registrar Cliente"):
                        gc = conecta_planilha()
                        gc.get_worksheet(3).append_row([datetime.now().strftime('%d/%m/%Y'), nome, fone, stt, "", "Portal Interno", corr])
                        st.success(f"Cliente registrado com sucesso por {st.session_state['user_logado']}!")
                        st.cache_data.clear()
                        st.rerun()

        elif menu == "🧠 People Analytics":
            st.title("🧠 People Analytics & Talentos")
            st.write("Análise de desempenho e clima organizacional.")
            # Radar de Competências (Exemplo fixo para visualização)
            fig_radar = go.Figure(data=go.Scatterpolar(r=[4, 5, 3, 4, 4], theta=['Vendas','Ética','Sistemas','Comunicação','Foco'], fill='toself'))
            st.plotly_chart(fig_radar)

        elif menu == "👥 Corretores":
            st.title("👥 Gestão de Corretores")
            st.dataframe(df_corr, use_container_width=True)

        elif menu == "💰 Vendas":
            st.title("💰 Histórico Financeiro e Comissões")
            st.dataframe(df_vendas_raw, use_container_width=True)

        elif menu == "📄 Currículos":
            st.title("📄 Banco de Talentos (R&S)")
            st.dataframe(df_cv, use_container_width=True)

    # --- TELAS PÚBLICAS ---
    else: 
        if menu == "🏠 Início":
            st.markdown("<h1 style='text-align: center; color: #007a7c; padding-top: 50px;'>Imobiliária Janeide Xavier LTDA</h1>", unsafe_allow_html=True)
            st.write("Portal interno de gestão e recrutamento.")
            
        elif menu == "🎯 Trabalhe Conosco":
            st.title("🎯 Faça parte do nosso time")
            with st.form("cv_pub"):
                n_cv = st.text_input("Nome")
                t_cv = st.text_input("Telefone")
                if st.form_submit_button("Enviar Currículo"):
                    gc = conecta_planilha()
                    gc.get_worksheet(2).append_row([datetime.now().strftime('%d/%m/%Y'), n_cv, t_cv, "Via Portal", "Interesse"])
                    st.success("Dados enviados!")

        elif menu == "🔐 Painel Restrito":
            st.subheader("Login Administrativo")
            u_input = st.text_input("Usuário").lower().strip()
            p_input = st.text_input("Senha", type="password")
            
            if st.button("Entrar", type="primary"):
                try:
                    users = st.secrets["credentials"]["usernames"]
                    if u_input in users and p_input == users[u_input]:
                        st.session_state["password_correct"] = True
                        st.session_state["user_logado"] = u_input
                        st.rerun()
                    else:
                        st.error("Dados incorretos.")
                except:
                    st.error("Erro na configuração de usuários (Secrets).")

    st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 11px; margin-top:50px;'>© 2026 ImobIJX | Atlas Intelligence</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
