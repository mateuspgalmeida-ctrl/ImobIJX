import streamlit as st
import pandas as pd
import numpy as np
import os
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# 1. FUNÇÃO DE CONEXÃO
def conecta_planilha():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(creds)
        return client.open("Dados_ImobIJX")
    except:
        return None

# 2. SISTEMA DE LOGIN E PÁGINA PÚBLICA
def main():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    # BARRA LATERAL PÚBLICA / PRIVADA
    with st.sidebar:
        if os.path.exists("logo.jpg"):
            st.image("logo.jpg", width=180)
        
        st.title("Menu ImobIJX")
        if st.session_state["password_correct"]:
            modo = st.radio("Navegação", ["📊 Dashboard", "👥 Equipe", "🏠 Vendas", "📄 Ver Currículos"])
            if st.button("Sair"):
                st.session_state["password_correct"] = False
                st.rerun()
        else:
            modo = st.radio("Navegação Pública", ["👋 Início", "📝 Trabalhe Conosco", "🔒 Área Administrativa"])

    # --- LÓGICA PÚBLICA ---
    if not st.session_state["password_correct"]:
        if modo == "👋 Início":
            st.title("Bem-vindo à ImobIJX")
            st.write("Excelência na gestão imobiliária.")
        
        elif modo == "📝 Trabalhe Conosco":
            st.title("Faça parte da nossa Equipe!")
            with st.form("form_cv"):
                nome_cv = st.text_input("Nome Completo")
                zap_cv = st.text_input("WhatsApp")
                exp_cv = st.text_area("Conte um pouco da sua experiência")
                link_cv = st.text_input("Link do seu currículo (Drive/LinkedIn)")
                enviar_cv = st.form_submit_button("Enviar Candidatura")
                
                if enviar_cv and nome_cv:
                    gc = conecta_planilha()
                    if gc:
                        # Salva na Aba 3 (índice 2)
                        sheet_cv = gc.get_worksheet(2)
                        sheet_cv.append_row([str(datetime.now()), nome_cv, zap_cv, exp_cv, link_cv])
                        st.success("Recebemos seu cadastro! Entraremos em contato.")

        elif modo == "🔒 Área Administrativa":
            st.subheader("Login para Gestores")
            user = st.text_input("Usuário")
            pw = st.text_input("Senha", type="password")
            if st.button("Entrar"):
                if user in st.secrets["credentials"]["usernames"] and pw == st.secrets["credentials"]["usernames"][user]:
                    st.session_state["password_correct"] = True
                    st.rerun()
                else:
                    st.error("Acesso negado.")

    # --- LÓGICA PRIVADA (SÓ APÓS LOGIN) ---
    else:
        gc = conecta_planilha()
        
        if modo == "📊 Dashboard":
            st.title("Dashboard Estratégico")
            c1, c2, c3 = st.columns(3)
            # Simulação de dados para o Dash (pode ler das abas depois)
            c1.metric("VGV Mensal", "R$ 1.2M", "+5%")
            c2.metric("Comissões", "R$ 72k")
            c3.metric("Novos CVs", "12")
            st.line_chart(np.random.randint(10, 50, 7), color="#007a7c")

        elif modo == "👥 Equipe":
            st.title("Gestão de Corretores")
            t1, t2 = st.tabs(["Cadastrar", "Lista"])
            with t1:
                with st.form("cad_corretor"):
                    n = st.text_input("Nome")
                    c = st.text_input("CRECI")
                    esp = st.selectbox("Perfil", ["Luxo", "Urbano", "Rural"])
                    if st.form_submit_button("Salvar"):
                        gc.get_worksheet(0).append_row([n, "", c, "", esp, ""])
                        st.success("Corretor Adicionado!")
            with t2:
                df = pd.DataFrame(gc.get_worksheet(0).get_all_records())
                st.dataframe(df)

        elif modo == "🏠 Vendas":
            st.title("Gestão de Vendas e Comissões")
            with st.form("venda_form"):
                corretores = [row['Nome'] for row in gc.get_worksheet(0).get_all_records()]
                c_venda = st.selectbox("Corretor", corretores if corretores else ["Nenhum"])
                valor = st.number_input("Valor do Imóvel", min_value=0.0)
                perc = st.slider("% Comissão Total", 0.0, 10.0, 6.0)
                if st.form_submit_button("Registrar Venda"):
                    total_com = valor * (perc/100)
                    repasse = total_com * 0.40 # Exemplo: 40% para o corretor
                    gc.get_worksheet(1).append_row([str(datetime.now()), c_venda, valor, total_com, repasse])
                    st.success(f"Venda registrada! Repasse Corretor: R$ {repasse:,.2f}")

        elif modo == "📄 Ver Currículos":
            st.title("Candidatos Interessados")
            df_cv = pd.DataFrame(gc.get_worksheet(2).get_all_records())
            st.dataframe(df_cv)

if __name__ == "__main__":
    main()
