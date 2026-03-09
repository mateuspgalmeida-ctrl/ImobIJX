import streamlit as st
import pandas as pd
import numpy as np
import os
import gspread
from google.oauth2.service_account import Credentials

# 1. FUNÇÃO DE SEGURANÇA (LOGIN)
def check_password():
    def password_entered():
        if (
            st.session_state["username"] in st.secrets["credentials"]["usernames"]
            and st.session_state["password"]
            == st.secrets["credentials"]["usernames"][st.session_state["username"]]
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.title("🔒 ImobIJX | Acesso Restrito")
        st.text_input("Usuário", on_change=password_entered, key="username")
        st.text_input("Senha", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.title("🔒 ImobIJX | Acesso Restrito")
        st.text_input("Usuário", on_change=password_entered, key="username")
        st.text_input("Senha", type="password", on_change=password_entered, key="password")
        st.error("❌ Usuário ou senha incorretos.")
        return False
    else:
        return True

# 2. EXECUÇÃO DO PORTAL (SÓ RODA SE LOGADO)
if check_password():
    # Toda a configuração do app agora fica "dentro" deste bloco
    
    # Estilo e Configuração
    st.markdown("""
        <style>
        .stApp { background-color: #f4f7f6; font-family: 'Inter', sans-serif; }
        .stButton>button { background-color: #007a7c; color: white; border-radius: 10px; font-weight: bold; width: 100%; }
        h1, h2, h3 { color: #004d4d; }
        </style>
        """, unsafe_allow_html=True)

    def conecta_planilha():
        try:
            scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
            creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
            client = gspread.authorize(creds)
            return client.open("Dados_ImobIJX")
        except Exception as e:
            st.error(f"Erro de conexão: {e}")
            return None

    # Barra Lateral
    with st.sidebar:
        if os.path.exists("logo.jpg"):
            st.image("logo.jpg", width=180)
        else:
            st.title("🏢 ImobIJX")
        
        st.markdown(f"**Bem-vindo(a) à Gestão de Elite**")
        menu = st.radio("MENU", ["📊 Dashboard", "👥 Equipe & Corretores", "🏠 Gestão de Vendas"])
        if st.button("Sair / Logoff"):
            del st.session_state["password_correct"]
            st.rerun()

    # Telas
    if menu == "📊 Dashboard":
        st.title("Painel Estratégico")
        st.write("Dados em tempo real da ImobIJX.")
        c1, c2 = st.columns(2)
        c1.metric("Status do Atlas", "Ativo 🤖")
        c2.metric("Banco de Dados", "Conectado ✅")

    elif menu == "👥 Equipe & Corretores":
        st.title("Gestão de Pessoas")
        tab1, tab2 = st.tabs(["➕ Cadastrar", "🔍 Consultar"])
        
        gc = conecta_planilha()
        
        with tab1:
            with st.form("novo_corretor"):
                nome = st.text_input("Nome")
                creci = st.text_input("CRECI")
                especialidade = st.selectbox("Área", ["Urbano", "Rural", "Luxo"])
                enviar = st.form_submit_button("Salvar na Planilha")
                if enviar and gc:
                    sheet = gc.get_worksheet(0)
                    sheet.append_row([nome, "", creci, "", especialidade, ""])
                    st.success("Salvo com sucesso!")

        with tab2:
            if gc:
                sheet = gc.get_worksheet(0)
                df = pd.DataFrame(sheet.get_all_records())
                st.table(df)

    elif menu == "🏠 Gestão de Vendas":
        st.title("Módulo de Vendas")
        st.info("Em breve: Cadastro de imóveis e cálculo de comissões.")

    st.markdown("<br><hr><center><b>ImobIJX</b> v1.8 | Admin: Mateus & Janeide</center>", unsafe_allow_html=True)
