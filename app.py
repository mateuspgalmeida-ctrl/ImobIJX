import streamlit as st
import pandas as pd
import numpy as np
import os

# 1. CONFIGURAÇÃO E ESTILO DE ALTA PERFORMANCE
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

# 2. BARRA LATERAL (ImobIJX)
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
    st.info("Atlas: Sistema Iniciado 🤖")

# 3. LÓGICA DAS TELAS

# --- TELA: DASHBOARD INICIAL ---
if menu == "📊 Dashboard Inicial":
    st.title("Dashboard Estratégico | ImobIJX")
    st.write("Bem-vindo, Mateus. Os indicadores abaixo serão atualizados conforme você cadastrar a produtividade.")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("VGV Total", "R$ 0,00", "Aguardando dados")
    c2.metric("Corretores", "0", "Nenhum cadastrado")
    c3.metric("Conversão", "0%", "N/A")
    c4.metric("Novos Leads", "0", "Mês Atual")
    
    st.info("ℹ️ Comece cadastrando sua equipe na aba 'Equipe & Corretores' para gerar os primeiros gráficos.")

# --- TELA: EQUIPE & CORRETORES ---
elif menu == "👥 Equipe & Corretores":
    st.title("Gestão de Pessoas | ImobIJX")
    
    tab_cadastro, tab_perfil, tab_prod = st.tabs([
        "➕ Cadastrar Novo Membro", 
        "🔍 Consultar Equipe", 
        "📈 Lançar Produtividade"
    ])
    
    # Inicializando lista vazia para a sessão
    if 'lista_corretores' not in st.session_state:
        st.session_state.lista_corretores = []

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
                especialidade = st.multiselect("Especialidades", ["Urbano", "Rural", "Luxo", "Minha Casa Minha Vida", "Lançamentos"])
                fone_n = st.text_input("WhatsApp")
            
            btn_salvar_n = st.form_submit_button("Finalizar Cadastro")
            if btn_salvar_n:
                if nome_n:
                    st.session_state.lista_corretores.append(nome_n)
                    st.success(f"Corretor {nome_n} cadastrado com sucesso!")
                    st.balloons()
                else:
                    st.error("Por favor, preencha o nome do corretor.")

    with tab_perfil:
        if not st.session_state.lista_corretores:
            st.warning("Nenhum corretor cadastrado ainda.")
        else:
            corretor_sel = st.selectbox("Selecione o profissional para ver detalhes:", st.session_state.lista_corretores)
            st.info(f"Ficha técnica de {corretor_sel} em processamento pelo Atlas.")

    with tab_prod:
        st.subheader("Registro Mensal de Resultados")
        if not st.session_state.lista_corretores:
            st.warning("Cadastre um corretor primeiro para poder lançar produtividade.")
        else:
            with st.form("form_prod_mensal", clear_on_submit=True):
                c_p = st.selectbox("Selecionar Corretor", st.session_state.lista_corretores)
                v_qtd = st.number_input("Vendas (Qtd)", min_value=0)
                vgv_l = st.number_input("VGV Total (R$)", min_value=0.0)
                btn_prod = st.form_submit_button("Salvar Resultados")
                if btn_prod:
                    st.success(f"Resultados de {c_p} salvos com sucesso!")

# --- DEMAIS TELAS ---
else:
    st.title(menu)
    st.info("Módulo pronto para receber seus dados da ImobIJX.")

# RODAPÉ
st.markdown("<br><hr><center><b>ImobIJX</b> v1.6 | Gestão sob medida para Mateus</center>", unsafe_allow_html=True)
