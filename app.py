import streamlit as st
import pandas as pd
import numpy as np
import os
import gspread
from google.oauth2.service_account import Credentials

# 1. CONFIGURAÇÃO E ESTILO
st.set_page_config(page_title="ImobIJX | Gestão Inteligente", layout="wide", page_icon="🏢")

st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e0e0e0; }
    .kpi-card {
        background-color: #ffffff; padding: 20px; border-radius: 15px;
        border-left: 5px solid #007a7c; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        text-align: center; margin-bottom: 20px;
    }
    .stButton>button {
        background-color: #007a7c; color: white; border-radius: 10px;
        border: none; height: 3em; width: 100%; font-weight: bold;
    }
    h1, h2, h3 { color: #004d4d; font-weight: 800; }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNÇÃO DE CONEXÃO COM GOOGLE SHEETS
def conecta_planilha():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        # Usa as credenciais salvas nos Secrets do Streamlit
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(creds)
        # Abre a planilha pelo nome exato
        return client.open("Dados_ImobIJX")
    except Exception as e:
        st.error(f"Erro na conexão com Google Sheets: {e}")
        return None

# 3. BARRA LATERAL
with st.sidebar:
    if os.path.exists("logo.jpg"):
        st.image("logo.jpg", width=180)
    else:
        st.title("🏢 ImobIJX")
    
    st.markdown("<br>", unsafe_allow_html=True)
    menu = st.radio("MENU PRINCIPAL", [
        "📊 Dashboard Inicial", 
        "🏠 Gestão de Vendas",
        "👥 Equipe & Corretores", 
        "🧠 People Analytics (Match)", 
        "📄 Cadastro de Currículos"
    ])
    st.markdown("---")
    st.info("Atlas: Banco de Dados Conectado 🗄️")

# 4. LÓGICA DAS TELAS

# --- TELA: DASHBOARD INICIAL ---
if menu == "📊 Dashboard Inicial":
    st.title("Dashboard Estratégico | ImobIJX")
    
    # Busca dados da planilha para os KPIs
    gc = conecta_planilha()
    if gc:
        try:
            # Pega todos os valores da primeira aba (Corretores)
            sheet_corretores = gc.get_worksheet(0)
            dados = sheet_corretores.get_all_records()
            df = pd.DataFrame(dados)
            total_corretores = len(df)
        except:
            total_corretores = 0
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("VGV Total", "R$ 0,00", "Aguardando Vendas")
    c2.metric("Corretores", total_corretores, "Cadastrados")
    c3.metric("Conversão", "0%", "N/A")
    c4.metric("Leads", "0", "Mês Atual")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Tendência de Performance")
    st.line_chart(np.random.randn(10, 1), color=["#007a7c"])

# --- TELA: EQUIPE & CORRETORES ---
elif menu == "👥 Equipe & Corretores":
    st.title("Gestão de Pessoas | ImobIJX")
    
    tab_cadastro, tab_lista, tab_prod = st.tabs([
        "➕ Cadastrar Novo Membro", 
        "🔍 Consultar Equipe", 
        "📈 Lançar Produtividade"
    ])
    
    gc = conecta_planilha()

    with tab_cadastro:
        st.subheader("Adicionar Novo Membro à ImobIJX")
        with st.form("form_novo_corretor", clear_on_submit=True):
            c_c1, c_c2 = st.columns(2)
            with c_c1:
                nome_n = st.text_input("Nome Completo")
                cpf_n = st.text_input("CPF")
                creci_n = st.text_input("CRECI")
            with c_c2:
                data_adm = st.date_input("Data de Início")
                espec_n = st.selectbox("Especialidade Principal", ["Urbano", "Rural", "Luxo", "MCMV", "Lançamentos"])
                fone_n = st.text_input("WhatsApp")
            
            btn_salvar = st.form_submit_button("Salvar na Planilha")
            
            if btn_salvar:
                if nome_n and gc:
                    sheet = gc.get_worksheet(0) # Salva na primeira aba
                    sheet.append_row([nome_n, cpf_n, creci_n, str(data_adm), espec_n, fone_n])
                    st.success(f"Corretor {nome_n} salvo permanentemente no Google Sheets!")
                    st.balloons()
                else:
                    st.error("Erro ao salvar. Verifique se o nome foi preenchido.")

    with tab_lista:
        if gc:
            sheet = gc.get_worksheet(0)
            df_equipe = pd.DataFrame(sheet.get_all_records())
            if not df_equipe.empty:
                st.dataframe(df_equipe, use_container_width=True)
            else:
                st.warning("Nenhum corretor na base de dados.")

    with tab_prod:
        st.subheader("Registrar Vendas/Captações")
        st.info("Módulo pronto para salvar na segunda aba da sua planilha.")

# --- DEMAIS TELAS ---
else:
    st.title(menu)
    st.info("Módulo sob gestão da ImobIJX.")

# RODAPÉ
st.markdown("<br><hr><center><b>ImobIJX</b> v1.7 | Dashboard com Banco de Dados Real</center>", unsafe_allow_html=True)
