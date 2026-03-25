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
    .status-tag {
        padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: bold;
    }
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
            st.success(f"Logado: {st.session_state.get('user_logado', 'Gestor')}")
            menu = st.radio("ADMINISTRAÇÃO", ["📊 Dashboard", "🤝 Clientes (CRM)", "🧠 People Analytics", "👥 Corretores", "💰 Vendas", "📄 Currículos"])
            
            st.divider()
            hoje = datetime.now()
            ano_sel = st.selectbox("Ano", [hoje.year, hoje.year-1], index=0)
            mes_sel_nome = st.selectbox("Mês", list(MESES_PT.values()), index=hoje.month-1)
            mes_sel_num = [k for k, v in MESES_PT.items() if v == mes_sel_nome][0]
            
            if st.button("🚪 Sair"):
                st.session_state["password_correct"] = False
                st.rerun()

    # --- CARGA DE DADOS ---
    df_corr = buscar_dados(0)
    df_vendas_raw = buscar_dados(1)
    df_cv = buscar_dados(2)
    df_clientes = buscar_dados(3) # ABA NOVA DE CLIENTES

    # --- LÓGICA DE TELAS ADMIN ---
    if st.session_state["password_correct"]:
        
        if menu == "📊 Dashboard":
            st.title(f"📊 Dashboard Estratégico - {mes_sel_nome}/{ano_sel}")
            
            # KPIs Rápidos
            c1, c2, c3, c4 = st.columns(4)
            vgv_total = df_vendas_raw['Valor'].apply(limpar_moeda).sum() if not df_vendas_raw.empty else 0
            qtd_clientes = len(df_clientes) if not df_clientes.empty else 0
            
            with c1: st.markdown(f'<div class="kpi-card"><p class="kpi-label">VGV Geral</p><p class="kpi-val">R$ {vgv_total:,.0f}</p></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="kpi-card"><p class="kpi-label">Base Clientes</p><p class="kpi-val">{qtd_clientes}</p></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="kpi-card"><p class="kpi-label">Leads Ativos</p><p class="kpi-val">{len(df_clientes[df_clientes["Status"]=="Lead"]) if qtd_clientes > 0 else 0}</p></div>', unsafe_allow_html=True)
            with c4: st.markdown(f'<div class="kpi-card"><p class="kpi-label">Corretores</p><p class="kpi-val">{len(df_corr)}</p></div>', unsafe_allow_html=True)

            st.divider()
            col_a, col_b = st.columns([2,1])
            with col_a:
                st.subheader("📈 Funil de Conversão (Clientes)")
                if not df_clientes.empty:
                    funil_data = df_clientes['Status'].value_counts().reindex(STATUS_CLIENTE).fillna(0)
                    fig_funil = px.funnel(x=funil_data.values, y=funil_data.index, color=funil_data.index, color_discrete_sequence=px.colors.qualitative.Teal)
                    st.plotly_chart(fig_funil, use_container_width=True)
            with col_b:
                st.subheader("🎨 Social Media")
                st.info("Dica: Use os dados do ranking para seus cards semanais.")
                if st.button("Gerar Card de Feedback"):
                    st.success("Card gerado na memória! (Simulação de integração Canva/Design)")

        elif menu == "🤝 Clientes (CRM)":
            st.title("🤝 Gestão de Relacionamento (CRM)")
            
            tab_lista, tab_novo = st.tabs(["📋 Carteira de Clientes", "➕ Novo Lead/Cliente"])
            
            with tab_lista:
                if not df_clientes.empty:
                    filtro_status = st.multiselect("Filtrar por Status", STATUS_CLIENTE, default=STATUS_CLIENTE)
                    df_c_filt = df_clientes[df_clientes['Status'].isin(filtro_status)]
                    st.dataframe(df_c_filt, use_container_width=True)
                else:
                    st.warning("Nenhum cliente cadastrado na aba 'Clientes' da planilha.")

            with tab_novo:
                with st.form("form_cliente"):
                    c1, c2 = st.columns(2)
                    nome_cl = c1.text_input("Nome do Cliente")
                    tel_cl = c2.text_input("WhatsApp")
                    status_cl = st.selectbox("Classificação", STATUS_CLIENTE)
                    interesse = st.selectbox("Interesse", ["Compra - Residencial", "Compra - Luxo", "Aluguel", "Terreno/Lote", "Investimento"])
                    corretor_resp = st.selectbox("Corretor Responsável", df_corr['Nome'].unique() if not df_corr.empty else ["Nenhum"])
                    
                    if st.form_submit_button("Salvar no CRM"):
                        gc = conecta_planilha()
                        if gc:
                            gc.get_worksheet(3).append_row([datetime.now().strftime('%d/%m/%Y'), nome_cl, tel_cl, status_cl, interesse, "Portal Interno", corretor_resp])
                            st.cache_data.clear()
                            st.success("Cliente adicionado com sucesso!")
                            st.rerun()

        elif menu == "🧠 People Analytics":
            st.title("🧠 People Analytics")
            st.write("Análise de Clima e Performance da Equipe")
            # Gráfico de Radar simulando competências médias da equipe
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(r=[4, 3, 5, 2, 4], theta=['Vendas','Processos','Foco','Sistemas','Comunicação'], fill='toself'))
            st.plotly_chart(fig_radar)

        elif menu == "👥 Corretores":
            st.title("👥 Gestão de Corretores")
            st.dataframe(df_corr, use_container_width=True)

        elif menu == "💰 Vendas":
            st.title("💰 Histórico de Vendas")
            st.dataframe(df_vendas_raw, use_container_width=True)

        elif menu == "📄 Currículos":
            st.title("📄 Banco de Talentos")
            st.dataframe(df_cv, use_container_width=True)
            st.divider()
            st.subheader("📝 Roteiro de Entrevista R&S")
            st.markdown("""
            1. **Qualificações:** Conte sobre seu histórico em vendas complexas.
            2. **Resiliência:** Como lida com o 'não' em uma negociação de alto valor?
            3. **Processo:** Qual sua rotina de prospecção diária?
            """)

    # --- TELAS PÚBLICAS ---
    else: 
        if menu == "🏠 Início":
            st.markdown("<h1 style='text-align: center; color: #007a7c; padding-top: 50px;'>Imobiliária Janeide Xavier LTDA</h1>", unsafe_allow_html=True)
            st.info("Acesse o Painel Restrito para gerenciar Leads, Vendas e Pessoas.")
            
        elif menu == "🎯 Trabalhe Conosco":
            st.title("🎯 Faça parte do nosso time")
            with st.form("cv_publico"):
                n = st.text_input("Nome")
                t = st.text_input("Telefone")
                e = st.selectbox("Experiência", ["Iniciante", "1-3 anos", "Especialista"])
                if st.form_submit_button("Enviar"):
                    gc = conecta_planilha()
                    gc.get_worksheet(2).append_row([datetime.now().strftime('%d/%m/%Y'), n, t, e, "Candidato via Portal"])
                    st.success("Recebido!")

        elif menu == "🔐 Painel Restrito":
            st.subheader("Login Administrativo")
            u = st.text_input("Usuário")
            p = st.text_input("Senha", type="password")
            if st.button("Acessar", type="primary"):
                if u in st.secrets["credentials"]["usernames"] and p == st.secrets["credentials"]["usernames"][u]:
                    st.session_state["password_correct"] = True
                    st.session_state["user_logado"] = u
                    st.rerun()
                else: st.error("Erro de acesso.")

    st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 11px; margin-top:50px;'>© 2026 ImobIJX | Atlas Intelligence</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
