import streamlit as st
import pandas as pd
import numpy as np
import os
import gspread
from google.oauth2.service_account import Credentials

# 1. FUNÇÃO DE LOGIN
def check_password():
    def password_entered():
        if (
            st.session_state["username"] in st.secrets["credentials"]["usernames"]
            and st.session_state["password"]
            == st.secrets["credentials"]["usernames"][st.session_state["username"]]
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Não guarda a senha
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.title("🔒 Acesso Restrito | ImobIJX")
        st.text_input("Usuário", on_change=password_entered, key="username")
        st.text_input("Senha", type="password", on_change=password_entered, key="password")
        st.info("Entre com suas credenciais para acessar o Atlas.")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Usuário", on_change=password_entered, key="username")
        st.text_input("Senha", type="password", on_change=password_entered, key="password")
        st.error("😕 Usuário ou senha incorretos.")
        return False
    else:
        return True

# SÓ EXECUTA O RESTANTE DO APP SE O LOGIN FOR SUCESSO
if check_password():
    # --- TODO O RESTANTE DO SEU CÓDIGO (CONFIGURAÇÃO, SIDEBAR, MENU) VEM AQUI DENTRO ---
    
    st.set_page_config(page_title="ImobIJX | Gestão Inteligente", layout="wide", page_icon="🏢")

    # [O restante do código que já tínhamos (conecta_planilha, menus, etc) continua aqui...]
    # Lembre-se de manter a indentação (espaços à esquerda) para tudo ficar dentro do 'if check_password()'
